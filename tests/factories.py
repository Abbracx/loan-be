import factory
from django.contrib.auth import get_user_model
from apps.loans.models import LoanApplication, FraudFlag

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class LoanApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LoanApplication

    user = factory.SubFactory(UserFactory)
    amount_requested = factory.Faker('pydecimal', left_digits=7, right_digits=2, positive=True)
    purpose = factory.Faker('text', max_nb_chars=200)


class FraudFlagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FraudFlag

    loan_application = factory.SubFactory(LoanApplicationFactory)
    reason = factory.Faker('sentence', nb_words=5)
