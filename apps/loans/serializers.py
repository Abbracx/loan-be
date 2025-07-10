from rest_framework import serializers
from .models import LoanApplication, FraudFlag


class FraudFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudFlag
        fields = ['reason']


class LoanApplicationSerializer(serializers.ModelSerializer):
    fraud_flags = FraudFlagSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = LoanApplication
        fields = [
            'pkid','id', 'amount_requested', 'purpose', 'status', 
            'date_applied', 'date_updated', 'fraud_flags', 'user_email'
        ]
        read_only_fields = ['pkid', 'status', 'date_applied', 'date_updated']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AdminLoanApplicationSerializer(LoanApplicationSerializer):
    class Meta(LoanApplicationSerializer.Meta):
        read_only_fields = ['date_applied', 'date_updated']
