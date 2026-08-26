from config import *
from make_context import make_context


def system_context():
    content = ""
    return make_context("system", content)