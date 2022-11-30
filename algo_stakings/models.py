from django.db import models

# Create your models here.


class Nfts(models.Model):
    assetId = models.IntegerField()
    ImageId = models.IntegerField()
    Uri = models.CharField(max_length=255)
    CD = models.DateTimeField()

    class Meta:
        db_table = 'nfts'


class NftsTransactions(models.Model):
    appId = models.IntegerField()
    txId = models.CharField(max_length=500)
    assetId = models.IntegerField()
    address = models.CharField(max_length=500)
    timeStamp = models.IntegerField()
    isClaimed = models.BooleanField()
    stakeId = models.IntegerField()
    CD = models.DateTimeField()

    class Meta:
        db_table = 'nfts_transactions'
