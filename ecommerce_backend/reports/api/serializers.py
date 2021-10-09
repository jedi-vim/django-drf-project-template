from rest_framework import serializers


class CommisionSalesPersonSerializer(serializers.Serializer):
    salesperson_id = serializers.IntegerField(required=True)
    begin = serializers.DateTimeField(required=True, write_only=True)
    end = serializers.DateTimeField(required=True, write_only=True)
    salesperson_name = serializers.CharField(read_only=True)
    total_comission = serializers.DecimalField(
        read_only=True, decimal_places=2, max_digits=9)


class SellablePurchasedRankingSerializer(serializers.Serializer):
    sellable_id = serializers.IntegerField(required=True)
    sellable_description = serializers.CharField(required=True)
    total_purchased = serializers.DecimalField(
        required=True, decimal_places=2, max_digits=9)
