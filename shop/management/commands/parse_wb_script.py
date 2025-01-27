import requests
from django.core.management import BaseCommand
from parser.parsing import ParseWB
from shop.models import Product, Category
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile


class Command(BaseCommand):
    help = "Run the Wildberries parser"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting the Wildberries parse"))
        try:
            parser = ParseWB(
                "https://www.wildberries.ru/catalog/208088292/detail.aspx?size=333603678"
            ).parse()

            for product_info in parser.products:
                slug = Product.generate_slug(product_info.name)
                image_links = product_info.image_links.split(";")
                if image_links:
                    image_url = image_links[0]
                    img_name = f"{slug}-main.jpg"
                    response = requests.get(image_url)
                    response.raise_for_status()
                    img_temp = NamedTemporaryFile()
                    img_temp.write(response.content)
                    img_temp.flush()

                    category = Category.objects.get(id=3)
                    db_product = Product.objects.create(
                        category=category,
                        title=product_info.name,
                        brand=product_info.brand,
                        description="",
                        price=product_info.salePriceU / 89,
                        discount=product_info.sale,
                    )
                    db_product.image.save(img_name, File(img_temp), save=True)

            self.stdout.write(self.style.SUCCESS("Parser completed successfully!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error:{e}"))