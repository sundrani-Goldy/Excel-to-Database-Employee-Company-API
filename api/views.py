from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import FileUploadSerializer, CompanySerializer, EmployeeSerializer
from .models import Company, Employee

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
                        "message": "Data imported successfully"
                    }
                }
            ),
            400: 'Bad Request'
        }
    )
    def create(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.create(serializer.validated_data)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        return self.serializer_class

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
