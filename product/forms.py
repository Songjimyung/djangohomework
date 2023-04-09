from django import forms
from .models import Product, Inbound


# 폼 만들어보기

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'price', 'size', 'quantity']


class InboundForm(forms.ModelForm):
    class Meta:
        model = Inbound
        fields = ['product', 'quantity']

    def __init__(self, *args, **kwargs):
        super(InboundForm, self).__init__(*args, **kwargs)
        self.fields['product'].empty_label = '상품을 선택해주세요.'

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')

        if not quantity:
            raise forms.ValidationError('수량을 입력해주세요.')

        if quantity < 0:
            raise forms.ValidationError('수량은 0 이상이어야 합니다.')

        return cleaned_data
