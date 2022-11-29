from rest_framework import serializers
from algo_stakings import models


class nftsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Nfts
        fields = "__all__"


class nftsTransactionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.NftsTransactions
        fields = "__all__"
