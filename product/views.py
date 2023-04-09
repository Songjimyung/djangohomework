from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Inbound, Outbound, Inventory
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import ProductForm, InboundForm
from django.contrib import messages
from django.db.models import Sum


# from django.db.models import Sum


# Create your views here.

def home(request):
    user = request.user.is_authenticated
    if user:
        return render(request, 'base.html')
    else:
        return redirect('/login')


# @login_required()
# def product_list(request):
#     products = Product.objects.all()
#     context = {'products': products}
#     return render(request, 'product/product_list.html', context)

# 폼을 활용한 상품리스트
@login_required()
def product_list(request):
    products = Product.objects.all()
    form = ProductForm()
    context = {'products': products, 'form': form}
    return render(request, 'product/product_list.html', context)


# @login_required()
# def product_create(request):
#     if request.method == 'POST':
#         code = request.POST['code']
#         name = request.POST['name']
#         description = request.POST['description']
#         price = request.POST['price']
#         size = request.POST['size']
#         quantity = request.POST['quantity']
#         product = Product(code=code, name=name, description=description, price=price, size=size, quantity=quantity)
#         product.save()
#         return redirect('/create')
#     else:
#         return render(request, 'product/product_create.html', {'sizes': Product.sizes})
@login_required()
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product-list')
    else:
        form = ProductForm()
    return render(request, 'product/product_create.html', {'form': form})


@login_required
@transaction.atomic  # 모두 실패, 혹은 모두 성공 되어야 커밋된 상태를 저장해줌
def inbound_create(request):
    if request.method == 'POST':
        # POST 요청에서 데이터를 받아와 처리하는 부분
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        # 상품 정보 가져오기
        product = Product.objects.get(id=product_id)

        # 입고 기록 생성
        inbound = Inbound.objects.create(product=product, quantity=quantity)

        # 입고 수량 조정
        product.quantity += int(quantity)
        product.save()
        inventory, _ = Inventory.objects.get_or_create(product=product)
        inventory.stock_quantity += int(quantity)
        inventory.save()
        # 입고 후 입고페이지 그대로
        return redirect('inbound-create')

    # GET 요청에 대한 처리
    # 상품 선택을 위한 form 표시
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'product/inbound_create.html', context)


# @login_required
# @transaction.atomic
# def inbound_create(request):
#     if request.method == 'POST':
#         form = InboundForm(request.POST)
#         if form.is_valid():
#             # 폼 데이터 유효성 검사
#             product = form.cleaned_data['product']
#             quantity = form.cleaned_data['quantity']
#             price = Product.price
#             inbound = Inbound.objects.create(product=product, quantity=quantity, price=price)
#
#             # 입고 수량 조정
#             product.price += quantity
#             product.save()
#
#             # 상품 상세 페이지로 이동
#             return redirect('product-list', pk=product.pk)
#     else:
#         form = InboundForm()
#
#     context = {'form': form}
#     return render(request, 'product/inbound_create.html', context)
# 폼 제대로 활용 실패 ㅠㅠ

@login_required
def outbound_create(request):
    # POST 요청일 때, 출고 기록 생성
    if request.method == 'POST':
        # 선택한 상품 ID를 가져옵니다.
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        # 선택한 상품 정보를 가져옵니다.
        product = Product.objects.get(id=product_id)

        # 출고 수량 검증
        if int(quantity) <= 0:
            messages.error(request, '수량은 0 이상이어야 합니다.')
            return redirect('outbound-create')

        outbound = Outbound.objects.create(product=product, quantity=quantity)

        # 상품의 재고 수량 조정

        product.quantity -= int(quantity)
        product.save()
        inventory, _ = Inventory.objects.get_or_create(product=product)
        inventory.stock_quantity -= int(quantity)
        inventory.save()

        return redirect('outbound-create')

        # GET 요청일 때, 상품을 선택할 수 있는 페이지 렌더링
        # 모든 상품 정보를 가져옵니다.
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'product/outbound_create.html', context)


# 근데 굳이 stock_quantity가 필요할까? product.quantity 값이 product의 재고값이니 총 재고..?
@login_required
def product_inventory(request, pk):
    product = get_object_or_404(Product, pk=pk)
    inventory, created = Inventory.objects.get_or_create(product=product)

    # 기존에 존재하는 Inventory인 경우, 해당 Inventory의 정보를 업데이트
    if not created:
        inventory.save()

    # 총 입고 수량, 가격 계산, aggregate()함수 사용 //Sum 함수 사용한 결과를 반환
    inbound_quantity = Inbound.objects.filter(product=product).aggregate(total_quantity=Sum('quantity'))[
                           'total_quantity'] or 0

    # 총 출고 수량, 가격 계산
    outbound_quantity = Outbound.objects.filter(product=product).aggregate(total_quantity=Sum('quantity'))[
                            'total_quantity'] or 0

    stock_quantity = inventory.stock_quantity

    context = {
        'product': product,
        'stock_quantity': stock_quantity,
        'inbound_quantity': inbound_quantity,
        'outbound_quantity': outbound_quantity,
    }
    return render(request, 'product/inventory.html', context)
