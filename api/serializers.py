from rest_framework import serializers
from .models import Company, Employee
import pandas as pd
from decimal import Decimal
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Employee
        fields = '__all__'

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    REQUIRED_COLUMNS = [
        'COMPANY_NAME', 'FIRST_NAME', 'LAST_NAME', 'PHONE_NUMBER',
        'EMPLOYEE_ID', 'MANAGER_ID', 'DEPARTMENT_ID', 'SALARY'
    ]

    @transaction.atomic
    def create(self, validated_data):
        file = validated_data['file']
        
        # Read the file
        try:
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                df = pd.read_csv(file)
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise serializers.ValidationError("Unable to read file. Please check format.")

        # Validate file content
        self._validate_file_content(df)
        
        # Process all the data
        unique_companies, employees_list, errors, duplicates = self._process_data(df)
        
        # Save companies in bulk
        companies_created = self._save_companies(unique_companies)
        
        # Get all companies we just created or already existed
        all_companies = {c.name: c for c in Company.objects.filter(name__in=unique_companies)}
        
        # Get existing employee IDs to avoid duplicates
        existing_ids = set(Employee.objects.filter(
            company__in=all_companies.values()
        ).values_list('employee_id', flat=True))
        
        # Prepare employee records for bulk creation
        employees_to_create = []
        for emp_data in employees_list:
            row = emp_data.pop('row')
            company_name = emp_data.pop('company_name')
            
            # Skip duplicates
            if emp_data['employee_id'] in existing_ids:
                duplicates.append({
                    "row": row,
                    "company": company_name,
                    "employee_id": emp_data['employee_id']
                })
                continue
                
            if company_name in all_companies:
                emp_data['company'] = all_companies[company_name]
                employees_to_create.append(Employee(**emp_data))
                existing_ids.add(emp_data['employee_id'])  # Mark as processed
        
        # Bulk create employees
        employees_created = 0
        if employees_to_create:
            try:
                Employee.objects.bulk_create(employees_to_create)
                employees_created = len(employees_to_create)
            except Exception as e:
                logger.error(f"Error creating employees: {e}")
                errors.append(f"Failed to create employees: {str(e)}")

        # Prepare response
        return self._prepare_response(companies_created, employees_created, errors, duplicates)

    def _validate_file_content(self, df):
        """Validate that file has all required columns and contains data."""
        # Check for required columns
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise serializers.ValidationError({
                "columns": f"Missing columns: {', '.join(missing_columns)}"
            })

        # Check if file has data
        if df.empty:
            raise serializers.ValidationError({"data": "File contains no data"})
    
    def _process_data(self, df):
        """Process dataframe rows and extract company and employee data."""
        unique_companies = set()
        employees_list = []
        errors = []
        duplicates = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Get and validate company name
                company_name = row['COMPANY_NAME']
                if not isinstance(company_name, str) or not company_name.strip():
                    errors.append({
                        "row": index + 2,
                        "error": "Invalid company name"
                    })
                    continue
                
                company_name = company_name.strip()
                unique_companies.add(company_name)
                
                # Prepare employee data
                employee = self._prepare_employee_data(row)
                employee['row'] = index + 2
                employee['company_name'] = company_name
                employees_list.append(employee)
                
            except Exception as e:
                errors.append({
                    "row": index + 2, 
                    "error": str(e)
                })
                
        return unique_companies, employees_list, errors, duplicates
    
    def _save_companies(self, company_names):
        """Save all unique companies in bulk."""
        # Get existing companies
        existing_companies = set(Company.objects.filter(
            name__in=company_names
        ).values_list('name', flat=True))
        
        # Create new companies
        new_companies = [Company(name=name) for name in company_names if name not in existing_companies]
        if new_companies:
            Company.objects.bulk_create(new_companies)
            
        return len(new_companies)
    
    def _prepare_employee_data(self, row):
        """Convert row data to employee fields."""
        # Validate salary
        salary = Decimal(str(row['SALARY']))
        if salary <= 0:
            raise ValueError("Salary must be positive")

        # Validate employee ID
        employee_id = int(row['EMPLOYEE_ID'])
        if employee_id <= 0:
            raise ValueError("Employee ID must be positive")

        # Return formatted employee data
        return {
            'first_name': str(row['FIRST_NAME']).strip(),
            'last_name': str(row['LAST_NAME']).strip(),
            'phone_number': str(row['PHONE_NUMBER']).strip(),
            'employee_id': employee_id,
            'manager_id': int(row['MANAGER_ID']),
            'department_id': int(row['DEPARTMENT_ID']),
            'salary': salary
        }
        
    def _prepare_response(self, companies_created, employees_created, errors, duplicates):
        """Format the final response."""
        response = {
            'message': 'File import completed',
            'statistics': {
                'companies_created': companies_created,
                'employees_created': employees_created,
            }
        }
        
        if errors:
            response['errors'] = errors
        
        if duplicates:
            response['duplicates'] = duplicates

        return response

    def validate_file(self, value):
        """Validate file type and size."""
        if not value.name.endswith(('.xlsx', '.csv')):
            raise serializers.ValidationError(
                "Unsupported file format. Only Excel (.xlsx) and CSV files are supported."
            )
            
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError(
                "File size too large. Maximum file size is 10MB."
            )
            
        return value