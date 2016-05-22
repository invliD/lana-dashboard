from rest_framework.serializers import ModelSerializer

from lana_dashboard.lana_data.models import Institution, IPv4Subnet


class InstitutionSerializer(ModelSerializer):
	class Meta:
		model = Institution
		fields = ['name', 'code', 'abuse_email']


class IPv4SubnetSerializer(ModelSerializer):
	institution = InstitutionSerializer()

	class Meta:
		model = IPv4Subnet
		fields = ['network', 'comment', 'institution']
