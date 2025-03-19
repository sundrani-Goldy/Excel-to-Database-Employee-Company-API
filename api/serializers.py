from rest_framework import serializers
from .models import Company, Employee
import pandas as pd

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

    def create(self, validated_data):
        file = validated_data['file']
        
        # Read the Excel file
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)

        # Group data by company
        company_groups = df.groupby('COMPANY_NAME')
        
        for company_name, company_data in company_groups:
            # Create company once
            company_serializer = CompanySerializer(data={'name': company_name})
            if company_serializer.is_valid(raise_exception=True):
                company = company_serializer.save()
            
            # Process all employees for this company
            for _, record in company_data.iterrows():
                employee_data = {
                    'company': company.id,
                    'first_name': record['FIRST_NAME'],
                    'last_name': record['LAST_NAME'],
                    'phone_number': record['PHONE_NUMBER'],
                    'employee_id': record['EMPLOYEE_ID'],
                    'manager_id': record['MANAGER_ID'],
                    'department_id': record['DEPARTMENT_ID'],
                    'salary': record['SALARY']
                }
                employee_serializer = EmployeeSerializer(data=employee_data)
                if employee_serializer.is_valid(raise_exception=True):
                    employee_serializer.save()

        return {'message': 'Data imported successfully'}

    def validate_file(self, value):
        if not value.name.endswith(('.xlsx', '.csv')):
            raise serializers.ValidationError("Only Excel (.xlsx) and CSV files are supported")
        return value
