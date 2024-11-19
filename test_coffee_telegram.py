import pytest
from coffee_telegram import handle_response
import asyncio

@pytest.mark.asyncio
def test_handle_response():
    response = asyncio.run(handle_response("oi"))
    assert response == "Oi, tudo bem? Como posso te atender?"
