from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Opportunity
from .serializers import OpportunitySerializer

@extend_schema(responses={200: OpportunitySerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_opportunities(request):
    """
    List all opportunities.
    """
    opportunities = Opportunity.objects.all()
    serializer = OpportunitySerializer(opportunities, many=True)
    return Response(serializer.data)

@extend_schema(request=OpportunitySerializer, responses={201: OpportunitySerializer})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_opportunity(request):
    """
    Create a new opportunity.
    """
    serializer = OpportunitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(posted_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(responses={200: OpportunitySerializer})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_opportunity(request, pk):
    """
    Get details of a single opportunity.
    """
    try:
        opportunity = Opportunity.objects.get(pk=pk)
    except Opportunity.DoesNotExist:
        return Response({"error": "Opportunity not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OpportunitySerializer(opportunity)
    return Response(serializer.data)
