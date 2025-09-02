from contextcounter import count_text, count_messages, get_context_limit, ContextInspector

def test_counts_text():
    assert count_text("hello") > 0

def test_counts_messages():
    msgs = [{"role":"system","content":"sys"},{"role":"user","content":"hi"}]
    assert count_messages(msgs, model="gpt-4o", provider="openai") >= 3

def test_inspector_limit():
    ctx = ContextInspector(provider="openai")
    limit = ctx.get_limit("gpt-4o")
    assert limit is None or limit >= 128000
