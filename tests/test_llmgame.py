"""Module to test the functions in blog module"""
import pytest
from llmgame.db import get_db


def test_index(client):
    """Root endpoint test"""
    response = client.get('/')
    assert b"AI Quizmaster" in response.data
    assert b"Begin" in response.data

