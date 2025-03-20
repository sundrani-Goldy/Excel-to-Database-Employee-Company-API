from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import FileUploadSerializer, CompanySerializer, EmployeeSerializer
from .models import Company, Employee
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class FileUploadViewSet(viewsets.ViewSet):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = FileUploadSerializer

    @swagger_auto_schema(
        operation_description="Upload an Excel or CSV file to import data",
        manual_parameters=[
            openapi.Parameter(
                'file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Excel or CSV file containing employee and company data'
            )
        ],
        responses={
            201: openapi.Response(
                description="Data imported successfully",
                examples={
                    "application/json": {
                        "message": "Data import completed",
                        "statistics": {
                            "companies_processed": 1,
                            "employees_processed": 10
                        },
                        "warnings": [
                            {
                                "row": 5,
                                "company": "Company Name",
                                "error": "Invalid employee data format"
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={
                    "application/json": {
                        "error": {
                            "file_format": "Unsupported file format",
                            "columns": "Missing required columns",
                            "data": "Validation error details"
                        }
                    }
                }
            ),
            413: "File too large",
            415: "Unsupported media type"
        }
    )
    def create(self, request):
        try:
            serializer = FileUploadSerializer(data=request.data)
            if serializer.is_valid():
                result = serializer.create(serializer.validated_data)
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(
                {"validation_error": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in file upload: {e}")
            return Response(
                {"error": "An unexpected error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_serializer_class(self):
        return self.serializer_class

class CompanyViewSet(viewsets.ViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @swagger_auto_schema(
        operation_description="Get list of all companies",
        responses={
            200: openapi.Response(
                description="Success",
                schema=CompanySerializer(many=True)
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    def list(self, request):
        companies = self.queryset.all()
        serializer = self.serializer_class(companies, many=True)
        return Response(serializer.data)

class EmployeeViewSet(viewsets.ViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @swagger_auto_schema(
        operation_description="Get list of all employees",
        responses={
            200: openapi.Response(
                description="Success",
                schema=EmployeeSerializer(many=True)
            ),
            400: "Bad Request", 
            500: "Internal Server Error"
        }
    )
    def list(self, request):
        employees = self.queryset.all()
        serializer = self.serializer_class(employees, many=True)
        return Response(serializer.data)
