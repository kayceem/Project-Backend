import random
from faker import Faker
import models
from database import SessionLocal
fake = Faker()

def create_users(session, n=50):
    for _ in range(n):
        user = models.User(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.sha256(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            contact_number=fake.random_number(digits=10, fix_len=True)
        )
        session.add(user)
    session.commit()

def create_categories(session, n=10):
    categories = [
    'Electronics', 'Clothing', 'Books', 'Toys', 'Sports', 'Furniture', 'Automotive', 'Beauty', 'Health', 'Groceries',
    'Garden', 'Appliances', 'Kitchen', 'Tools', 'Pet Supplies', 'Arts & Crafts', 'Jewelry', 'Musical Instruments',
    'Movies & TV', 'Software', 'Office Products', 'Baby Products', 'Shoes', 'Watches', 'Home Improvement',
    'Patio & Outdoor', 'Video Games', 'Computers', 'Cameras', 'Phones', 'Luggage & Travel', 'Collectibles',
    'Stationery', 'Gift Cards', 'Industrial & Scientific'
]
    for i in range(n):
        category = models.Category(
            name=categories[i],
            description=fake.text()
        )
        session.add(category)
    session.commit()

def create_products(session, n=50):
    users = session.query(models.User).all()
    categories = session.query(models.Category).all()

    for _ in range(n):
        product = models.Product(
            user_id=random.choice(users).id,
            category_id=random.choice(categories).id,
            title=fake.sentence(),
            description=fake.text(),
            price=round(random.uniform(1, 1000), 2),
            image_url=fake.image_url(),
            views=random.randint(0, 1000)
        )
        session.add(product)
    session.commit()


def create_reviews(session, n=50):
    users = session.query(models.User).all()

    for _ in range(n):
        reviewer, reviewee = random.sample(users, 2)
        review = models.Review(
            reviewer_id=reviewer.id,
            reviewee_id=reviewee.id,
            rating=random.randint(1, 5),
            comment=fake.text()
        )
        session.add(review)
    session.commit()

def create_messages(session, n=50):
    users = session.query(models.User).all()

    for _ in range(n):
        sender, receiver = random.sample(users, 2)
        message = models.Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=fake.text()
        )
        session.add(message)
    session.commit()

def create_wishlist_items(session, n=50):
    users = session.query(models.User).all()
    products = session.query(models.Product).all()
    added_pair = set()
    for _ in range(n):
        user = random.choice(users)
        product = random.choice(products)
        pair = (user.id, product.id)
        if pair in added_pair:
            continue
        exists = session.query(models.WishListItem).filter_by(user_id=user.id, product_id=product.id).first()
        if exists:
            continue
        wishlist_item = models.WishListItem(
            user_id=user.id,
            product_id=product.id
        )
        session.add(wishlist_item)
        added_pair.add(pair)
    session.commit()

def generate_data(session):
    create_users(session, 100)
    create_categories(session,20)
    create_products(session,40)
    create_reviews(session, 50)
    create_messages(session,200)
    create_wishlist_items(session, 120)

with SessionLocal() as session:
    generate_data(session)