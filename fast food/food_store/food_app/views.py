from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Food, FoodType, Like, Comment
from .forms import FoodForm, FoodTypeForm

# Main page view
def main_page(request):
    # Barcha ovqatlarni va kategoriyalarni olish
    foods = Food.objects.all()
    food_types = FoodType.objects.all()

    # Filtr uchun tanlangan kategoriya
    selected_type = request.GET.get('type')
    if selected_type:
        foods = foods.filter(food_type__id=selected_type)

    return render(request, 'food_app/main_page.html', {
        'foods': foods,
        'food_types': food_types,
    })

# Restricted to users with 'add_foodtype' permission
@permission_required('food_app.add_foodtype', raise_exception=True)
@login_required
def add_food_type(request):
    if request.method == 'POST':
        form = FoodTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New food type added successfully')
            return redirect('main_page')
    else:
        form = FoodTypeForm()
    return render(request, 'food_app/add_food_type.html', {'form': form})

# Restricted to users with 'add_food' permission
@permission_required('food_app.add_food', raise_exception=True)
@login_required
def add_food(request):
    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.view_count = 0  # Boshlang'ich ko'rishlar soni
            food.like_count = 0  # Boshlang'ich like'lar soni
            food.save()
            messages.success(request, 'New food added successfully')
            return redirect('main_page')
    else:
        form = FoodForm()
    return render(request, 'food_app/add_food.html', {'form': form})

# Like a food (no special permission required)
@login_required
def like_food(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    like, created = Like.objects.get_or_create(user=request.user, food=food)
    
    if not created:
        # Agar like mavjud bo'lsa, o'chiramiz
        like.delete()
        food.like_count -= 1
        messages.info(request, f'You unliked {food.name}')
    else:
        # Agar like qo'yilmagan bo'lsa, qo'shamiz
        food.like_count += 1
        messages.success(request, f'You liked {food.name}')
    food.save()

    return redirect('main_page')

# Add comment to a food (no special permission required)
@login_required
def add_comment(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        Comment.objects.create(user=request.user, food=food, content=content)
        messages.success(request, 'Comment added successfully')
        return redirect('main_page')
    return render(request, 'food_app/add_comment.html', {'food': food})

# Profile view for logged-in users
@login_required
def profile(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']

        # Foydalanuvchining ma'lumotlarini yangilash
        user = request.user
        user.username = username
        user.email = email
        user.save()

        messages.success(request, 'Profile updated successfully')
        return redirect('profile')

    return render(request, 'food_app/profile.html', {'user': request.user})

# User login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in!')
            return redirect('main_page')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'food_app/login.html')

# User registration view
def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password == password_confirm:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(username=username, password=password)
                messages.success(request, 'Account created successfully! You can now log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'food_app/register.html')

# User logout view
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('login')

def food_detail(request, food_id):
    # Ovqatni olish va ko‘rishlar sonini oshirish
    food = get_object_or_404(Food, id=food_id)
    food.view_count += 1
    food.save()  # Ko'rishlar sonini yangilab saqlash

    # Tegishli izohlarni olish
    comments = Comment.objects.filter(food=food)

    return render(request, 'food_app/food_detail.html', {
        'food': food,
        'comments': comments,
    })