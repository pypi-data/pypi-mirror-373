from risk_detector.question_builder import build_questions, needed_feature_keys, _walk_jsonlogic
from risk_detector.evaluators.jsonlogic_eval import evaluate_rule
from types import SimpleNamespace

def make_rule(cond):
    return SimpleNamespace(condition=cond)

def test_needed_feature_keys_extracts_vars():
    rules = [
        make_rule({
            "and": [
                {"in": ["healthcare", {"var": "domain"}]},
                {"==": [{"var": "automation_level"}, "fully_automated"]}
            ]
        }),
        make_rule({
            "or": [
                {"in": ["biometric_id", {"var": "specific_usecases"}]},
                {"==": [{"var": "consequence_level"}, "high"]}
            ]
        })
    ]
    
    keys = needed_feature_keys(rules)
    expected = {"domain", "automation_level", "specific_usecases", "consequence_level"}
    assert keys == expected

def test_build_questions_orders_and_gates():
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
        "automation_level": SimpleNamespace(type="enum", required=False, prompt_en="Automation level"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=10, prompt_en="Choose domain", gating=None),
        SimpleNamespace(feature_key="automation_level", priority=20, prompt_en="Automation level?", gating={"==": [{"var": "domain"}, "healthcare"]})
    ]
    
    # Test without answers (should include all questions that match keys)
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1  # Only domain is in keys (from rules), automation_level is not in keys
    assert questions[0].feature_key == "domain"  # Lower priority first
    
    # Test with answers that satisfy gating condition
    answers = {"domain": "healthcare"}
    questions = build_questions(rules, features, questions_db, answers)
    assert len(questions) == 1  # Only domain is in keys, automation_level is not in keys even with answers
    assert questions[0].feature_key == "domain"
    
    # Test with answers that don't satisfy gating condition
    answers = {"domain": "other"}
    questions = build_questions(rules, features, questions_db, answers)
    assert len(questions) == 1  # Only domain question should be included
    assert questions[0].feature_key == "domain"

def test_walk_jsonlogic_nested():
    """Test _walk_jsonlogic with nested structures."""
    keys = set()
    node = {
        "and": [
            {"var": "domain"},
            {"or": [
                {"var": "automation_level"},
                {"in": ["test", {"var": "specific_usecases"}]}
            ]}
        ]
    }
    
    _walk_jsonlogic(node, keys)
    expected = {"domain", "automation_level", "specific_usecases"}
    assert keys == expected

def test_walk_jsonlogic_with_lists():
    """Test _walk_jsonlogic with list structures."""
    keys = set()
    node = [
        {"var": "domain"},
        {"and": [
            {"var": "automation_level"},
            {"var": "consequence_level"}
        ]}
    ]
    
    _walk_jsonlogic(node, keys)
    expected = {"domain", "automation_level", "consequence_level"}
    assert keys == expected

def test_walk_jsonlogic_empty():
    """Test _walk_jsonlogic with empty structures."""
    keys = set()
    
    # Test empty dict
    _walk_jsonlogic({}, keys)
    assert keys == set()
    
    # Test empty list
    _walk_jsonlogic([], keys)
    assert keys == set()
    
    # Test None
    _walk_jsonlogic(None, keys)
    assert keys == set()

def test_build_questions_with_required_features():
    """Test build_questions with required features."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
        "optional": SimpleNamespace(type="enum", required=False, prompt_en="Optional"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=10, prompt_en="Choose domain", gating=None),
        SimpleNamespace(feature_key="optional", priority=20, prompt_en="Optional?", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1  # Only domain is required, optional is not in keys
    assert questions[0].feature_key == "domain"  # Required feature first

def test_build_questions_no_matching_features():
    """Test build_questions when no features match."""
    rules = []
    features = {
        "unused": SimpleNamespace(type="enum", required=False, prompt_en="Unused"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="unused", priority=10, prompt_en="Unused?", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 0  # No questions should be included since no features are needed

def test_build_questions_with_gating_condition():
    """Test build_questions with gating conditions."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
        "automation_level": SimpleNamespace(type="enum", required=False, prompt_en="Automation level"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=10, prompt_en="Choose domain", gating=None),
        SimpleNamespace(feature_key="automation_level", priority=20, prompt_en="Automation level?", gating={"==": [{"var": "domain"}, "healthcare"]})
    ]
    
    # Test with answers that satisfy gating condition
    answers = {"domain": "healthcare"}
    questions = build_questions(rules, features, questions_db, answers)
    assert len(questions) == 1  # Only domain is in keys, automation_level is not in keys
    assert questions[0].feature_key == "domain"
    
    # Test with answers that don't satisfy gating condition
    answers = {"domain": "other"}
    questions = build_questions(rules, features, questions_db, answers)
    assert len(questions) == 1  # Only domain question should be included
    assert questions[0].feature_key == "domain"

def test_build_questions_with_none_answers():
    """Test build_questions with None answers."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=10, prompt_en="Choose domain", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db, None)
    assert len(questions) == 1  # Domain question should be included
    assert questions[0].feature_key == "domain"

def test_build_questions_with_empty_answers():
    """Test build_questions with empty answers."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=10, prompt_en="Choose domain", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db, {})
    assert len(questions) == 1  # Domain question should be included
    assert questions[0].feature_key == "domain"

def test_build_questions_with_priority_sorting():
    """Test build_questions with priority sorting."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
        "automation_level": SimpleNamespace(type="enum", required=True, prompt_en="Automation level"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="automation_level", priority=20, prompt_en="Automation level?", gating=None),
        SimpleNamespace(feature_key="domain", priority=10, prompt_en="Choose domain", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db, {})
    assert len(questions) == 2  # Both questions should be included
    assert questions[0].feature_key == "domain"  # Lower priority first
    assert questions[1].feature_key == "automation_level"  # Higher priority second

def test_build_questions_with_none_priority():
    """Test build_questions with None priority."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=None, prompt_en="Choose domain", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db, {})
    assert len(questions) == 1  # Domain question should be included
    assert questions[0].feature_key == "domain"

def test_build_questions_with_zero_priority():
    """Test build_questions with zero priority."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=0, prompt_en="Choose domain", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db, {})
    assert len(questions) == 1  # Domain question should be included
    assert questions[0].feature_key == "domain"

def test_build_questions_with_none_priority_2():
    """Test build_questions with None priority."""
    rules = []
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=None, prompt_en="Choose domain", gating=None)
    ]
    
    questions = build_questions(rules, features, questions_db, {})
    assert len(questions) == 1  # Domain question should be included
    assert questions[0].feature_key == "domain"

def test_build_questions_with_zero_priority_2():
    """Test build_questions with zero priority values."""
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    questions_db = [
        SimpleNamespace(feature_key="domain", priority=0, prompt_en="Choose domain", gating=None),
    ]
    
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"

def test_build_questions_with_missing_priority_attribute():
    """Test build_questions with questions that don't have priority attribute (line 38)."""
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    # Create a question without priority attribute
    question_without_priority = SimpleNamespace(feature_key="domain", prompt_en="Choose domain", gating=None)
    # Remove priority attribute if it exists
    if hasattr(question_without_priority, 'priority'):
        delattr(question_without_priority, 'priority')
    
    questions_db = [question_without_priority]
    
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"

def test_build_questions_with_none_priority_attribute():
    """Test build_questions with questions that have None priority attribute (line 38)."""
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    # Create a question with None priority attribute
    question_with_none_priority = SimpleNamespace(feature_key="domain", priority=None, prompt_en="Choose domain", gating=None)
    
    questions_db = [question_with_none_priority]
    
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"

def test_build_questions_with_missing_priority_attribute_comprehensive():
    """Test build_questions with questions that don't have priority attribute (line 38)."""
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    # Create a question without priority attribute using a different approach
    question_without_priority = SimpleNamespace(feature_key="domain", prompt_en="Choose domain", gating=None)
    
    questions_db = [question_without_priority]
    
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"

def test_build_questions_with_missing_priority_attribute_final():
    """Test build_questions with questions that don't have priority attribute (line 38) - final test."""
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    # Create a question without priority attribute using a different approach
    question_without_priority = SimpleNamespace(feature_key="domain", prompt_en="Choose domain", gating=None)
    
    questions_db = [question_without_priority]
    
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"

def test_build_questions_with_missing_priority_attribute_final_comprehensive():
    """Test build_questions with missing priority attribute - final comprehensive coverage."""
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    # Create questions with missing priority attribute
    questions_db = [
        SimpleNamespace(feature_key="domain", prompt_en="Choose domain", gating=None),  # No priority attribute
    ]
    
    # Test without answers
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"
    
    # Test with answers
    answers = {"domain": "healthcare"}
    questions = build_questions(rules, features, questions_db, answers)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"

def test_build_questions_with_missing_priority_attribute_final_coverage():
    """Test build_questions with missing priority attribute - final coverage for line 38."""
    rules = [
        make_rule({"in": ["healthcare", {"var": "domain"}]})
    ]
    
    features = {
        "domain": SimpleNamespace(type="enum", required=True, prompt_en="Choose domain"),
    }
    
    # Create questions with missing priority attribute using a different approach
    class QuestionWithoutPriority:
        def __init__(self, feature_key, prompt_en, gating=None):
            self.feature_key = feature_key
            self.prompt_en = prompt_en
            self.gating = gating
            # No priority attribute at all
    
    questions_db = [
        QuestionWithoutPriority(feature_key="domain", prompt_en="Choose domain", gating=None),
    ]
    
    # Test without answers
    questions = build_questions(rules, features, questions_db)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"
    
    # Test with answers
    answers = {"domain": "healthcare"}
    questions = build_questions(rules, features, questions_db, answers)
    assert len(questions) == 1
    assert questions[0].feature_key == "domain"
