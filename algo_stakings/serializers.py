from rest_framework import serializers
from algo_stakings import models


class nftsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Nfts
        fields = "__all__"


class nftsTransactionsSerializer(serializers.ModelSerializer):
    Uri  = serializers.SerializerMethodField(method_name="get_uri")
    
    def get_uri(self, obj):
        return models.Nfts.objects.filter(assetId = obj.assetId).values("Uri")[0]["Uri"]
    class Meta:
        model = models.NftsTransactions
        fields = (
            "appId",
            "txId",
            "assetId",
            "address",
            "timeStamp",
            "isClaimed",
            "stakeId",
            "CD",
            "Uri"
        )