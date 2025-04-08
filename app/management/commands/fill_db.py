from django.core.management.base import BaseCommand
from django.db import connection
from faker import Faker
from app.models import Question, Answer, Tag, User, AnswerLike, QuestionLike, Profile
import random
import time

from app.views import question


class Command(BaseCommand):
    help = "Fill the database with test data. Requires a 'ratio' argument."
    faker = Faker('ru_RU')

    def add_arguments(self, parser):
        parser.add_argument(
            "ratio",
            type=int,
            help="Number indicating the data generation ratio"
        )

    def handle(self, *args, **kwargs):
        ratio = kwargs["ratio"]
        t = time.time()
        self.generate_tags(ratio)
        self.generate_users(ratio)
        self.generate_profiles(ratio)
        self.generate_questions(ratio * 10)
        self.bind_tags_to_questions()
        self.generate_answers(ratio * 100)
        self.generate_question_likes(ratio * 200)
        self.generate_answer_likes(ratio * 200)
        print(time.time() - t)

    def generate_tags(self, ratio):
        Tag.objects.all().delete()
        tags = []
        for _ in range(ratio):
            tag = Tag(name=self.faker.word() + "_" + str(random.randint(0, 1000000000)) )
            tags.append(tag)
        Tag.objects.bulk_create(tags)
        self.faker.unique.clear()

    def generate_users(self, ratio):
        User.objects.all().delete()
        users = []
        for _ in range(ratio):
            user = User(username=self.faker.word() + "_" + str(random.randint(0, 100000000)), email=self.faker.email(), password=self.faker.password(), first_name=self.faker.first_name(), last_name=self.faker.last_name())
            users.append(user)
        User.objects.bulk_create(users)

    def generate_questions(self, ratio):
        Question.objects.all().delete()
        questions = []
        users = User.objects.all()
        for _ in range(ratio):
            question = Question(title=self.faker.sentence(nb_words=3) + " " + str(random.randint(0, 1000000000000)), text=self.faker.sentence(), author=random.choice(users))
            questions.append(question)
        Question.objects.bulk_create(questions)

    def bind_tags_to_questions(self):
        questions = Question.objects.all()
        tags = Tag.objects.all()
        for question in questions:
            question.tags.set(random.choices(tags, k=random.randint(1,3)))

    def generate_answers(self, ratio):
        Answer.objects.all().delete()
        answers = []
        questions = Question.objects.all()
        users = User.objects.all()
        for _ in range(ratio):
            answer = Answer(text=self.faker.sentence(nb_words=3), question=random.choice(questions), author=random.choice(users), is_correct=(random.random() > 0.9))
            answers.append(answer)
        Answer.objects.bulk_create(answers)

    def generate_profiles(self, ratio):
        Profile.objects.all().delete()
        profiles = []
        users=User.objects.all()
        for user in users:
            profile = Profile(user=user, avatar=random.choice(["img/kitten.jpg", "img/puppy.jpg"]))
            profiles.append(profile)
        Profile.objects.bulk_create(profiles)

    def generate_question_likes(self, ratio):
        QuestionLike.objects.all().delete()
        question_likes = []
        questions = Question.objects.all()
        users = User.objects.all()
        seen = set()
        for _ in range(ratio):
            qstn = random.choice(questions)
            usr = random.choice(users)
            while (qstn, usr) in seen:
                qstn = random.choice(questions)
                usr = random.choice(users)
            seen.add((qstn, usr))
            question_like = QuestionLike(question=qstn, user=usr, value=random.choice([-1, 1]))
            question_likes.append(question_like)
        QuestionLike.objects.bulk_create(question_likes)

    def generate_answer_likes(self, ratio):
        AnswerLike.objects.all().delete()
        answer_likes = []
        answers = Answer.objects.all()
        users = User.objects.all()
        seen = set()
        for _ in range(ratio):
            ans = random.choice(answers)
            usr = random.choice(users)
            while (ans, usr) in seen:
                ans = random.choice(answers)
                usr = random.choice(users)
            seen.add((ans, usr))
            answer_like = AnswerLike(answer=ans, user=usr, value=random.choice([-1, 1]))
            answer_likes.append(answer_like)
        AnswerLike.objects.bulk_create(answer_likes)
