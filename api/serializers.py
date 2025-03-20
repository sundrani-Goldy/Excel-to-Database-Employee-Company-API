from rest_framework import serializers
from .models import Company, Employee
import pandas as pd
from decimal import Decimal, InvalidOperation
import logging

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

    def create(self, validated_data):
        try:
            file = validated_data['file']
            
            # Read the Excel/CSV file
            try:
                if file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    df = pd.read_csv(file)
            except Exception as e:
                logger.error(f"File reading error: {e}")
                raise serializers.ValidationError(
                    "Unable to read the file. Please ensure it's a valid Excel or CSV file."
                )

            # Validate required columns
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
            if missing_columns:
                raise serializers.ValidationError({
                    "columns": f"Missing required columns: {', '.join(missing_columns)}"
                })

            # Check for empty dataframe
            if df.empty:
                raise serializers.ValidationError({
                    "data": "The uploaded file contains no data"
                })

            # Group data by company
            company_groups = df.groupby('COMPANY_NAME')
            
            processed_companies = 0
            processed_employees = 0
            errors = []
            duplicates = []
            
            for company_name, company_data in company_groups:
                if not isinstance(company_name, str) or not company_name.strip():
                    errors.append({
                        "company": "Invalid company name found"
                    })
                    continue

                try:
                    # Check if company exists
                    company_name = company_name.strip()
                    company = Company.objects.filter(name=company_name).first()
                    
                    if not company:  # Only create if company doesn't exist
                        # Create company
                        company_serializer = CompanySerializer(data={'name': company_name})
                        if company_serializer.is_valid(raise_exception=True):
                            company = company_serializer.save()
                            processed_companies += 1
                    
                    # Process employees
                    for index, record in company_data.iterrows():
                        try:
                            employee_data = self._prepare_employee_data(record, company)
                            
                            # Check if employee exists
                            existing_employee = Employee.objects.filter(
                                company=company,
                                employee_id=employee_data['employee_id']
                            ).first()
                            
                            if not existing_employee:  # Only create if employee doesn't exist
                                employee_serializer = EmployeeSerializer(data=employee_data)
                                if employee_serializer.is_valid():
                                    employee_serializer.save(company=company)
                                    processed_employees += 1
                                else:
                                    logger.error(f"Employee validation error: {employee_serializer.errors}")
                                    errors.append({
                                        "row": index + 2,
                                        "company": company_name,
                                        "employee_id": employee_data['employee_id'],
                                        "error": employee_serializer.errors
                                    })
                            else:
                                duplicates.append({
                                    "row": index + 2,
                                    "company": company_name,
                                    "employee_id": employee_data['employee_id'],
                                    "message": "Employee already exists"
                                })
                        except (ValueError, InvalidOperation) as e:
                            errors.append({
                                "row": index + 2,
                                "company": company_name,
                                "error": str(e)
                            })

                except Exception as e:
                    logger.error(f"Company processing error: {e}")
                    errors.append({
                        "company": company_name,
                        "error": f"Failed to process company data: {str(e)}"
                    })

            response = {
                'message': 'Data import completed',
                'statistics': {
                    'companies_processed': processed_companies,
                    'employees_processed': processed_employees,
                }
            }
            
            if errors:
                response['warnings'] = errors
            
            if duplicates:
                response['duplicates'] = duplicates

            return response

        except Exception as e:
            logger.error(f"File processing error: {e}")
            raise serializers.ValidationError({
                "error": "An unexpected error occurred while processing the file"
            })

    def _prepare_employee_data(self, record, company):
        try:
            salary = Decimal(str(record['SALARY']))
            if salary <= 0:
                raise ValueError("Invalid salary value")

            employee_id = int(record['EMPLOYEE_ID'])
            if employee_id <= 0:
                raise ValueError("Invalid employee ID")

            return {
                'first_name': str(record['FIRST_NAME']).strip(),
                'last_name': str(record['LAST_NAME']).strip(),
                'phone_number': str(record['PHONE_NUMBER']).strip(),
                'employee_id': employee_id,
                'manager_id': int(record['MANAGER_ID']),
                'department_id': int(record['DEPARTMENT_ID']),
                'salary': salary
            }
        except (ValueError, TypeError):
            raise ValueError("Invalid data format")

    def validate_file(self, value):
        if not value.name.endswith(('.xlsx', '.csv')):
            raise serializers.ValidationError({
                "file_format": "Unsupported file format. Only Excel (.xlsx) and CSV files are supported"
            })
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError({
                "file_size": "File size too large. Maximum file size is 10MB"
            })
        return value
