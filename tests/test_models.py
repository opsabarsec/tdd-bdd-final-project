# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, DataValidationError, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that the ID of the product object is not None
        # after calling the create() method.
        self.assertIsNotNone(product.id)
        # Fetch the product back from the system using the product ID
        # and store it in found_product
        found = Product.find(product.id)
        # Assert that the properties of the found_product match with the
        # properties of the original product object, such as
        # id, name, description and price.
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)

    def test_update_a_product(self):
        """It should update a product"""
        product = ProductFactory()
        print("this product is", product)
        product.id = None
        product.create()
        # Assert that the ID of the product object is not None
        # after calling the create() method.
        self.assertIsNotNone(product.id)
        # Fetch all the product back from the system.
        products = Product.all()
        # Assert the length of the products list is equal to 1
        # to verify that after updating the product, there is only
        # one product in the system.
        product.description = "my own description"
        original_id = product.id
        product.update()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        my_product = products[0]
        # Assert that the fetched product has id same as the original id.
        self.assertEqual(my_product.id, product.id)
        self.assertEqual(my_product.description, "my own description")
        # assert that change was only for data, no id
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(my_product.id, original_id)
        self.assertEqual(my_product.description, "my own description")
        # update without id, added to reach 95% coverage
        my_product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        # create a product
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product
        product.delete()
        # check it has been deleted
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It returns a list of all products"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        # create products pulling them with
        # a for loop
        num_products = 8
        for _ in range(8):
            product = ProductFactory()
            product.create()
        # now the lenght should be equal
        # to the number of products created
        products = Product.all()
        self.assertEqual(len(products), num_products)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        name_product = products[0].name
        count = len([product for product in products if product.name == name_product])

        found = Product.find_by_name(name_product)
        # Assert if the count of the found products matches the expected count.
        # Use a for loop to iterate over the found products and
        # assert that each product's name matches the expected name,
        # to ensure that all the retrieved products have the correct name.
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name_product)

    def test_find_by_availability(self):
        """It should Find a Product availability"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        availability_product = products[0].available
        count = len([product for product in products if product.available == availability_product])

        found = Product.find_by_availability(availability_product)
        # Assert if the count of the found products matches the expected count.
        # Use a for loop to iterate over the found products
        self.assertEqual(found.count(), count)
        # availability should match
        for product in found:
            self.assertEqual(product.available, availability_product)
            self.assertIsInstance(product.available, bool)

    def test_find_by_category(self):
        """It should Find a Product by category"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        category_product = products[0].category
        count = len([product for product in products if product.category == category_product])

        found = Product.find_by_category(category_product)
        # Assert if the count of the found products matches the expected count.
        # Use a for loop to iterate over the found products
        self.assertEqual(found.count(), count)
        # category should match
        for product in found:
            self.assertEqual(product.category, category_product)

    def test_find_by_price(self):
        """It should Find a Product by price"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()

        price_product = products[0].price

        count = len([product for product in products if product.price == price_product])

        found = Product.find_by_price(price_product)
        self.assertRaises(TypeError, Product.find_by_price(['']))
        # Assert if the count of the found products matches the expected count.
        # Use a for loop to iterate over the found products
        self.assertEqual(found.count(), count)
        # category should match
        for product in found:
            self.assertEqual(product.price, price_product)
