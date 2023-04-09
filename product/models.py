from django.db import models
from django.db.models import Sum


class Product(models.Model):
    class Meta:
        db_table = "product"

    code = models.IntegerField()
    name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    sizes = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('F', 'Free'),
    )
    size = models.CharField(choices=sizes, max_length=1)
    quantity = models.IntegerField()

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        # 수량이 0이 되면 삭제되게? 우선은 보류
        # if self.quantity == 0:
        #     self.delete()
        # else:
        super(Product, self).save(*args, **kwargs)


class Inbound(models.Model):
    """
    입고 모델.
    상품, 수량 필드를 작성.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inbound_product')
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name}, {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Outbound(models.Model):
    """
    출고 모델입니다.
    상품, 수량 필드를 작성합시다.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='outbound_product')
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name}, {self.quantity}원"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Inventory(models.Model):
    """
    창고의 제품과 수량 정보를 담는 모델입니다.
    상품, 수량 필드를 작성합니다.
    작성한 Product 모델을 OneToOne 관계로 작성합시다.
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} - {self.stock_quantity}"

    # 재고량 갱신

    def save(self, *args, **kwargs):
        outbound_quantity = Outbound.objects.filter(product=self.product).aggregate(total_quantity=Sum('quantity'))[
                                'total_quantity'] or 0
        inbound_quantity = Inbound.objects.filter(product=self.product).aggregate(total_quantity=Sum('quantity'))[
                               'total_quantity'] or 0
        self.stock_quantity = self.product.quantity + inbound_quantity - outbound_quantity
        super().save(*args, **kwargs)
