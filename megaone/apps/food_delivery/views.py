from django.views.generic import TemplateView

 
index_view = TemplateView.as_view(template_name="food-delivery/index.html")
food_accounts_view = TemplateView.as_view(template_name="food-delivery/accounts.html")
login_view = TemplateView.as_view(template_name="food-delivery/login.html")
registration_view = TemplateView.as_view(template_name="food-delivery/registration.html")
restaurant_detail_view = TemplateView.as_view(template_name="food-delivery/restaurant-detail.html")
restaurant_listing_view = TemplateView.as_view(template_name="food-delivery/restaurant-listing.html")