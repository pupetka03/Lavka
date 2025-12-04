from django.test import TestCase
from django.urls import path, re_path
from django.shortcuts import redirect
# Create your tests here.





def test(request):
    print("fff")
    previous_url = request.META.get('HTTP_REFERER', '/')
    

    if previous_url:
        print(f"Користувач прийшов зі сторінки: {previous_url}")
        # Тут можна виконати потрібну логіку
    else:
        print("Попередня сторінка не визначена (можливо, прямий перехід або інший сайт)")



    return redirect(previous_url)




