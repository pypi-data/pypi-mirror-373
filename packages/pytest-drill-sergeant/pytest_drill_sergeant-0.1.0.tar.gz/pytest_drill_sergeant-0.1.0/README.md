# 🎖️ Pytest Drill Sergeant

<!-- CI/CD Battle Status -->
[![CI Status](https://github.com/jeffrichley/pytest-drill-sergeant/workflows/CI%20(nox)/badge.svg)](https://github.com/jeffrichley/pytest-drill-sergeant/actions)
[![codecov](https://codecov.io/gh/jeffrichley/pytest-drill-sergeant/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffrichley/pytest-drill-sergeant)
[![Quality Gate](https://img.shields.io/badge/quality-A%2B-brightgreen?style=flat&logo=codacy)](https://github.com/jeffrichley/pytest-drill-sergeant)

<!-- Package Battle Metrics -->
[![PyPI version](https://badge.fury.io/py/pytest-drill-sergeant.svg)](https://badge.fury.io/py/pytest-drill-sergeant)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-drill-sergeant.svg)](https://pypi.org/project/pytest-drill-sergeant/)
[![Downloads](https://pepy.tech/badge/pytest-drill-sergeant)](https://pepy.tech/project/pytest-drill-sergeant)

<!-- Platform Combat Readiness -->
[![Platforms](https://img.shields.io/badge/platforms-Linux%20%7C%20macOS%20%7C%20Windows-blue)](https://github.com/jeffrichley/pytest-drill-sergeant/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- Military Honors & Achievements -->
[![Tested](https://img.shields.io/badge/battle--tested-6%20environments-red?style=flat&logo=pytest)](https://github.com/jeffrichley/pytest-drill-sergeant/actions)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue?style=flat&logo=python)](https://github.com/jeffrichley/pytest-drill-sergeant)
[![Drill Sergeant Approved](https://img.shields.io/badge/drill%20sergeant-approved%20%F0%9F%8E%96%EF%B8%8F-brightgreen)](https://github.com/jeffrichley/pytest-drill-sergeant)

**LISTEN UP, MAGGOTS! 🗣️**

Your test suite is a DISASTER! Tests scattered everywhere like a tornado hit your codebase, no markers, no structure, and don't even get me started on your "AAA" pattern that looks more like "Aaahhh-what-am-I-even-testing" pattern.

**The Drill Sergeant is here to whip your tests into shape!** 💪

This pytest plugin will turn your chaotic test mess into a disciplined, well-organized military formation. No mercy. No exceptions. Only QUALITY.

## 🏅 Live Battle Intelligence (Auto-Updating Intel)

| **Metric** | **Live Status** | **Military Assessment** |
|------------|-----------------|-------------------------|
| **📦 Codebase Size** | [![Files](https://img.shields.io/github/directory-file-count/jeffrichley/pytest-drill-sergeant/src?label=source%20files&logo=python&color=blue)](https://github.com/jeffrichley/pytest-drill-sergeant) | *"Lean and mean - no bloat allowed!"* |
| **⭐ Bug Reports** | [![GitHub issues](https://img.shields.io/github/issues/jeffrichley/pytest-drill-sergeant?label=open%20issues&logo=github)](https://github.com/jeffrichley/pytest-drill-sergeant/issues) | *"Zero tolerance for battlefield failures!"* |
| **📈 Activity Level** | [![Commits](https://img.shields.io/github/commit-activity/m/jeffrichley/pytest-drill-sergeant?label=monthly%20commits&logo=git&color=green)](https://github.com/jeffrichley/pytest-drill-sergeant) | *"Active military operations in progress!"* |
| **⚡ Response Time** | [![GitHub last commit](https://img.shields.io/github/last-commit/jeffrichley/pytest-drill-sergeant?label=last%20deployment&logo=github-actions)](https://github.com/jeffrichley/pytest-drill-sergeant) | *"Always ready for action!"* |
| **🎯 Stars Earned** | [![GitHub stars](https://img.shields.io/github/stars/jeffrichley/pytest-drill-sergeant?label=stars&logo=github&color=yellow)](https://github.com/jeffrichley/pytest-drill-sergeant) | *"Recognition from fellow soldiers!"* |

**The Drill Sergeant's Live Record:** *"All systems operational, zero compromises accepted!"* 🎖️

## 🎯 What This Bad Boy Does

- **🏷️ Automatic Marker Detection** - Because apparently you can't be trusted to add `@pytest.mark.unit` yourself
- **📝 AAA Structure Enforcement** - "Arrange-Act-Assert" not "Arrange-Act-And-Hope-It-Works"  
- **💥 Comprehensive Error Messages** - So detailed even your manager could understand what you did wrong
- **🚨 Zero Tolerance Policy** - One violation = one failed test. NO EXCEPTIONS!

## 🚀 Installation (AKA Basic Training)

### For Smart Developers

```bash
# Development dependency (where it belongs, recruit!)
uv add --group dev pytest-drill-sergeant

# Or if you're still using that ancient pip thing...
pip install pytest-drill-sergeant
```

### For "Special" Developers

```bash
# Runtime dependency (really? You need test quality enforcement in production?)
uv add pytest-drill-sergeant
```

## 🎖️ Advanced Arsenal (Secret Weapons Unlocked)

[![AAA Structure](https://img.shields.io/badge/AAA-Arrange%20Act%20Assert-blue?style=for-the-badge&logo=checkmarx)](https://github.com/jeffrichley/pytest-drill-sergeant)
[![Auto Detection](https://img.shields.io/badge/Auto--Detection-16%20Built--in%20Mappings-green?style=for-the-badge&logo=target)](https://github.com/jeffrichley/pytest-drill-sergeant)
[![Synonyms](https://img.shields.io/badge/Synonyms-Given%2FWhen%2FThen%20Support-purple?style=for-the-badge&logo=language)](https://github.com/jeffrichley/pytest-drill-sergeant)
[![Zero Config](https://img.shields.io/badge/Zero--Config-Ready%20to%20Deploy-orange?style=for-the-badge&logo=rocket)](https://github.com/jeffrichley/pytest-drill-sergeant)

## 📏 Before vs After (Prepare to be AMAZED)

### Before: Your Disaster Zone 🔥

```python
# tests/whatever/test_something.py (what kind of name is that?!)
def test_thing():
    x = Calculator()
    result = x.add(1, 2)
    assert result == 3  # Wow, such insight. Much test. Very quality.
```

**Drill Sergeant says:** *WHAT IS THIS GARBAGE? No marker, no structure, and it's in a random directory! This test FAILS until you fix it!*

### After: PROPER MILITARY FORMATION 🎖️

```python
# tests/unit/test_calculator.py (NOW we're talking!)
import pytest

@pytest.mark.unit  # AUTOMATIC! The Sergeant detects from directory and adds this! 🎯
def test_addition_with_positive_numbers():
    """Test addition functionality with positive integers."""
    # Arrange - Set up your battlefield, soldier!
    calculator = Calculator()
    first_operand = 5
    second_operand = 3
    expected_sum = 8
    
    # Act - Execute the mission!
    actual_sum = calculator.add(first_operand, second_operand)
    
    # Assert - Verify victory conditions!
    assert actual_sum == expected_sum
```

**Drill Sergeant says:** *OUTSTANDING! This is what DISCIPLINE looks like!*

### For Simple Tests (One-Liner AAA)

Sometimes your test is so simple that combining AAA sections makes sense:

```python
@pytest.mark.unit
def test_simple_calculation():
    """Test basic arithmetic operation."""
    # Arrange and Act - Set up calculator and perform addition
    result = Calculator().add(2, 3)
    
    # Assert - Verify the calculation is correct
    assert result == 5

@pytest.mark.unit  
def test_ultra_simple():
    """Test with all AAA in one comment (for the truly lazy)."""
    # Arrange, Act, and Assert - Create, call, and verify in one swift motion
    assert Calculator().multiply(4, 2) == 8
```

**Drill Sergeant says:** *Fine, soldier. Sometimes efficiency trumps ceremony. But don't get TOO comfortable!*

## 🎖️ Automatic Marker Detection (Because You're Lazy)

The Drill Sergeant isn't just here to yell at you - he's here to HELP. Place your tests in the right directories and watch the magic happen:

| Directory | Auto-Applied Marker | What It Means |
|-----------|-------------------|---------------|
| `tests/unit/` | `@pytest.mark.unit` | Fast, isolated tests |
| `tests/integration/` | `@pytest.mark.integration` | Tests multiple components |
| `tests/e2e/` | `@pytest.mark.e2e` | End-to-end user scenarios |
| `tests/api/` | `@pytest.mark.integration` | API endpoint tests |
| `tests/performance/` | `@pytest.mark.performance` | Speed/load tests |
| `tests/smoke/` | `@pytest.mark.integration` | Quick sanity checks |

**16 built-in mappings** so you don't have to think too hard! 🧠  
*(I've seen you think, and it ain't pretty!)*

### How It Works

1. **You write a test** (hopefully)
2. **Forget to add a marker** (as usual)  
3. **Drill Sergeant detects directory** (`tests/unit/test_foo.py`)
4. **AUTOMATICALLY MODIFIES your test function** to add `@pytest.mark.unit`
5. **Test passes as if you had added the marker yourself** 🎭
6. **You look competent** (even though the Sergeant did the work)

## 🔧 Configuration (For Control Freaks)

### The Nuclear Option: Turn Everything Off

```ini
# pytest.ini
[tool:pytest]
drill_sergeant_enabled = false
```

**Drill Sergeant says:** *You're on your own, soldier. Don't come crying when your tests are garbage.*

### Selective Enforcement (Baby Steps)  
*When you can't handle the full military experience and need training wheels* 🚲

```ini
# pytest.ini
[tool:pytest]
drill_sergeant_enforce_markers = true      # YES! ENFORCE THE MARKERS!
drill_sergeant_enforce_aaa = false         # Fine, be sloppy with your structure
drill_sergeant_auto_detect_markers = true  # Let me do your job for you
drill_sergeant_min_description_length = 5  # At least TRY to be descriptive
```

### Custom Mappings (For Special Snowflakes)

```ini
# pytest.ini
[tool:pytest]
# Format: directory_name=marker_name (maps test directories to pytest markers)
drill_sergeant_marker_mappings = contract=api,smoke=integration,load=performance
# Translation for civilians: 
# tests/contract/ → @pytest.mark.api
# tests/smoke/ → @pytest.mark.integration
# tests/load/ → @pytest.mark.performance
```

Or via environment (because you love complexity):

```bash
# Same format: directory=marker pairs
export DRILL_SERGEANT_MARKER_MAPPINGS="widget=unit,gizmo=integration"
# For those who need it spelled out: 
# tests/widget/ → @pytest.mark.unit
# tests/gizmo/ → @pytest.mark.integration
```

## 🎭 Error Messages That Don't Suck

When you inevitably mess up, the Drill Sergeant doesn't just say "test failed" like some amateur plugin. Oh no. You get the FULL TREATMENT:

```
❌ CODE QUALITY: Test 'test_disaster' violates project standards by missing test annotations and missing AAA structure
📋 3 requirement(s) must be fixed before this test can run:

🏷️  MISSING TEST CLASSIFICATION:
   • Add @pytest.mark.unit, @pytest.mark.integration, or move test to appropriate directory structure

📝 MISSING AAA STRUCTURE (Arrange-Act-Assert):
   • Add '# Arrange - description of what is being set up' comment before test setup
   • Add '# Act - description of what action is being performed' comment before test action

ℹ️  This is a PROJECT REQUIREMENT for all tests to ensure:
   • Consistent test structure and readability
   • Proper test categorization for CI/CD pipelines
   • Maintainable test suite following industry standards

📚 For examples and detailed requirements:
   • https://github.com/jeffrichley/pytest-drill-sergeant
   • pytest.ini (for valid markers)
```

**Translation:** *Your test is bad and you should feel bad. Here's exactly how to fix it.*

## 🎪 Configuration Examples (Real World Scenarios)

### The "I'm New Here" Setup

```ini
# pytest.ini - Training wheels ON
[tool:pytest]
drill_sergeant_enabled = true
drill_sergeant_enforce_markers = false     # Baby steps
drill_sergeant_enforce_aaa = true          # Learn structure first
drill_sergeant_auto_detect_markers = true  # Let the magic happen
```

### The "CI/CD Enforcer" Setup

```ini
# pytest.ini - NO MERCY in production
[tool:pytest]
drill_sergeant_enabled = true
drill_sergeant_enforce_markers = true      # ZERO TOLERANCE
drill_sergeant_enforce_aaa = true          # PERFECT STRUCTURE
drill_sergeant_auto_detect_markers = false # Do it yourself, lazy!
```

### The "Legacy Codebase Survival" Setup

```ini
# pytest.ini - Gradual improvement without mass suicide
[tool:pytest]
drill_sergeant_enabled = true
drill_sergeant_enforce_markers = false     # Skip marker enforcement for now
drill_sergeant_enforce_aaa = true          # Fix structure first
drill_sergeant_auto_detect_markers = true  # Auto-add markers where possible
```

## 🎨 Environment Variables (For the DevOps Heroes)

Control the Drill Sergeant from your environment like a puppet master:

```bash
# Turn the drill sergeant into a teddy bear
export DRILL_SERGEANT_ENABLED=false

# Make him extra mean about markers
export DRILL_SERGEANT_ENFORCE_MARKERS=true

# Demand War and Peace level descriptions
export DRILL_SERGEANT_MIN_DESCRIPTION_LENGTH=50

# Custom directory mappings for your special setup
export DRILL_SERGEANT_MARKER_MAPPINGS="widgets=unit,chaos=stress"
```

## 🎭 AAA Synonym Recognition (Because Apparently You're All Special Snowflakes! ❄️)

### The Problem: "You're Too Good for Military Vocabulary" 😤

Oh, so the Drill Sergeant's perfectly good vocabulary isn't fancy enough for you? You can't be bothered to learn basic military terminology that's been battle-tested across thousands of codebases? 

**Let me guess:**
- "Arrange" is too *corporate* for your hip startup? 🙄
- "Act" doesn't capture your *artistic vision* of test methodology? 🎨
- "Assert" sounds too *aggressive* for your safe space codebase? 🏳️

**Fine. FINE!** The Drill Sergeant will swallow his pride and learn your precious little words. But don't think for a second that lowering his standards to accommodate your delicate sensibilities makes him happy about it.

### The Solution: Synonym Recognition (AKA "Participation Trophy Mode") 🏆

*Against his better judgment*, the Sergeant can be taught new vocabulary. He'll grumble about it, but he'll do it. Because apparently "professional military standards" aren't good enough for you people.

#### Enable This Madness:

```ini
# pytest.ini - Enabling the coddling of your fragile vocabulary preferences
[tool:pytest]
drill_sergeant_aaa_synonyms_enabled = true  # *Heavy military sighing* 😮‍💨
```

#### Built-in Synonyms (Because I Apparently Have to Do Everything for You):

**Arrange Synonyms:** Setup, Given, Prepare, Initialize, Configure, Create, Build  
*"Setup? SETUP?! It's called ARRANGE! But sure, let's use baby words..."*

**Act Synonyms:** Call, Execute, Run, Invoke, Perform, Trigger, When  
*"I suppose 'When' is more gentle than 'Act'. Wouldn't want to trigger anyone..."*

**Assert Synonyms:** Verify, Check, Expect, Validate, Confirm, Ensure, Then  
*"Oh, we can't 'Assert' things anymore? Too confrontational? My mistake, let's 'gently verify'..."*

#### Now These ALL Work! (God Help Us All) 🎉

```python
def test_user_authentication():
    # Setup user credentials and mock database
    user = User(username="test_user")
    
    # Call the authentication service 
    result = auth_service.authenticate(user.username, "password123")
    
    # Verify successful authentication
    assert result.success is True
```

**Drill Sergeant internal monologue:** *"'Setup'... 'Call'... 'Verify'... What's next, 'Pretty please test my code'? In my day, we had STANDARDS! But nooooo, everyone's a special butterfly with their own vocabulary..."* 🦋

```python  
def test_bdd_style():
    # Given a valid shopping cart with items
    cart = ShoppingCart()
    cart.add_item("widget", price=10.00)
    
    # When calculating the total price
    total = cart.calculate_total()
    
    # Then the result should include tax
    assert total == 10.80  # 8% tax included
```

**Drill Sergeant:** *"Oh look, BDD! 'Given/When/Then' - how PRECIOUS! Let me guess, you also use 'user stories' instead of requirements and call bugs 'opportunities for improvement'? Next you'll want me to validate your feelings instead of your code!"* 💅

#### Custom Synonyms (For Extra Special Snowflakes):

Oh, the built-in synonyms aren't unique enough for you? You need your OWN PERSONAL vocabulary? Of course you do. 🙄

```ini
# pytest.ini - Because you're just THAT special
drill_sergeant_aaa_arrange_synonyms = Background,Precondition,Setup
drill_sergeant_aaa_act_synonyms = Execute,Trigger,Action  
drill_sergeant_aaa_assert_synonyms = Expect,Outcome,Result
```

*"Let me guess - your team is 'different' and 'innovative' and needs custom words to express your unique testing philosophy? Can't just use the same words as literally everyone else in the industry?"*

```python
def test_with_custom_vocabulary():
    # Background - Configure the test environment  
    api_client = APIClient(base_url="https://test.api.com")
    
    # Execute - Trigger the user creation endpoint
    response = api_client.create_user({"name": "John", "email": "john@test.com"})
    
    # Expect - Result should be successful user creation
    assert response.status_code == 201
    assert response.json()["user"]["name"] == "John"
```

**Drill Sergeant:** *"'Background'? 'Execute'? 'Expect'? What are you, writing poetry? It's a TEST, not a haiku! But fine, I'll learn your artisanal vocabulary. Just don't expect me to like it."* 📝

#### Environment Variable Control (For the Control Freaks):

Because apparently config files are too mainstream for you? You need ENVIRONMENT VARIABLES? 🌍

```bash
# Enable this circus of accommodation
export DRILL_SERGEANT_AAA_SYNONYMS_ENABLED=true

# Reject all my hard work and use only your precious custom words
export DRILL_SERGEANT_AAA_BUILTIN_SYNONYMS=false

# Define your team's "unique" vocabulary (eye roll intensifies)
export DRILL_SERGEANT_AAA_ARRANGE_SYNONYMS="Setup,Given,Background"
export DRILL_SERGEANT_AAA_ACT_SYNONYMS="When,Call,Execute"
export DRILL_SERGEANT_AAA_ASSERT_SYNONYMS="Then,Verify,Check"
```

*"Oh sure, let's make it even MORE complicated! Why have one place to configure things when you can have seventeen different ways? This is why we can't have nice things."* 🤦‍♂️

#### Backward Compatibility (Because I'm Not a Complete Monster): ✅

Look, I may be bitter about this whole "synonym accommodation" situation, but I'm not going to break your existing code. I have SOME integrity left.

- **Default: DISABLED** - Because I refuse to enable this madness by default
- **Original keywords always work** - "Arrange/Act/Assert" will NEVER be deprecated (unlike my dignity)
- **Explicit opt-in** - You have to ASK for this nonsense explicitly
- **Layered configuration** - Environment variables override pytest.ini because apparently you need 47 ways to configure everything

**The Drill Sergeant's Reluctant Promise:** *"Fine, I'll learn your fancy words. BUT - and this is a big BUT - whether you say 'Arrange', 'Setup', 'Given', or 'Pretty-please-configure-my-test', you WILL STILL write descriptive comments! I may have bent on vocabulary, but I will NEVER compromise on quality! Got it, recruit?!"* 🎖️

*Mutters under breath: "Setup... Given... what's next, 'Lovingly prepare the test environment'? Kids these days..."* 😤

## 🎯 Advanced Usage (Graduate Level)

### Custom Test Structure

```python
# tests/widgets/test_widget_factory.py
# Using the custom mapping from above: DRILL_SERGEANT_MARKER_MAPPINGS="widgets=unit"

def test_widget_creation_with_custom_colors():  # No marker needed! Auto-detected as @pytest.mark.unit
    """Test widget factory creates widgets with specified colors."""
    # Arrange - Prepare the widget factory and color specifications
    factory = WidgetFactory()
    desired_color = Color.NEON_PINK
    expected_widget_count = 1
    
    # Act - Request widget creation with custom color
    created_widgets = factory.create_widgets(
        count=expected_widget_count,
        color=desired_color
    )
    
    # Assert - Verify widget meets specifications
    assert len(created_widgets) == expected_widget_count
    assert created_widgets[0].color == desired_color
    assert created_widgets[0].is_properly_initialized()
```

### Complex AAA with Sub-sections

```python
@pytest.mark.integration
def test_user_authentication_flow():
    """Test complete user authentication including edge cases."""
    # Arrange - Set up test environment and dependencies
    # Database setup
    test_db = create_test_database()
    user_service = UserService(test_db)
    
    # Test user data
    valid_email = "test@example.com"
    valid_password = "SecurePassword123!"
    
    # Mock external services
    email_service = Mock(spec=EmailService)
    
    # Act - Execute the authentication flow
    registration_result = user_service.register_user(
        email=valid_email,
        password=valid_password,
        email_service=email_service
    )
    
    # Assert - Verify all expectations are met
    # Registration success
    assert registration_result.success is True
    assert registration_result.user_id is not None
    
    # Database state
    stored_user = test_db.get_user_by_email(valid_email)
    assert stored_user is not None
    assert stored_user.email == valid_email
    
    # External service interactions
    email_service.send_welcome_email.assert_called_once()
```

## 🎪 Troubleshooting (When Things Go Wrong)

### "The Drill Sergeant is Too Mean!"

**Problem:** Every test fails with quality violations.  
**Solution:** Your tests actually ARE garbage. Fix them or lower the standards:

```ini
drill_sergeant_enforce_aaa = false  # Give up on structure
drill_sergeant_min_description_length = 1  # Accept "a" as description
```

### "Auto-detection Isn't Working!"

**Problem:** Tests in `tests/unit/` aren't getting `@pytest.mark.unit`.  
**Solution:** Check your directory structure, genius:

```bash
# Wrong (no auto-detection)
tests/
  random_stuff/
    test_unit_something.py

# Right (auto-detects @pytest.mark.unit)
tests/
  unit/
    test_something.py
```

### "I Don't Want Markers!"

**Problem:** You hate organization and progress.  
**Solution:** Turn off marker enforcement:

```ini
drill_sergeant_enforce_markers = false
```

### "The Error Messages Are Too Verbose!"

**Problem:** You don't like helpful feedback.  
**Solution:** There is no solution. Embrace the verbosity. Learn from it. Grow as a developer.

## 🎖️ Contributing (Join the Army)

Want to make the Drill Sergeant even more ruthless? We accept contributions!

### Development Setup

```bash
# Clone the repo (obviously)
git clone https://github.com/jeffrichley/pytest-drill-sergeant.git
cd pytest-drill-sergeant

# Install with development dependencies
uv sync

# Run tests (they better all pass!)
just test

# Check quality (no excuses for sloppy code)
just quality

# See all available commands
just --list
```

### Development Commands

```bash
just test          # Run all tests
just test-unit     # Run only unit tests  
just test-integration  # Run integration tests
just lint          # Check code style
just type-check    # Verify type annotations
just quality       # Run all quality checks
just clean         # Clean up generated files
```

## 📊 Why This Plugin Exists

**Real talk:** I got tired of reviewing pull requests where tests looked like someone threw code at a wall and hoped it stuck. Tests without markers, no structure, comments like `# test stuff` - it was chaos.

The Drill Sergeant fixes this by:

1. **Making quality automatic** - Can't forget markers if they're added automatically
2. **Teaching good habits** - Clear error messages explain what quality looks like  
3. **Enforcing standards** - No more "we'll fix it later" (spoiler: later never comes)
4. **Being helpful** - Auto-detection means less work for developers who do things right

## 🎯 Philosophy

- **Quality is not negotiable** - Your tests represent your code quality
- **Structure creates clarity** - AAA pattern makes tests readable and maintainable
- **Consistency enables scale** - Markers and structure let teams work together
- **Automation prevents regression** - What can be automated should be automated

## 🔮 Future Features (Coming Soon™)

- **🎨 Custom AAA patterns** - Define your own test structure requirements
- **📊 Quality metrics** - Dashboard showing test quality across your codebase  
- **🤖 AI-powered suggestions** - Smart recommendations for test improvements
- **🔗 IDE integration** - Real-time quality feedback while you type
- **📈 Historical tracking** - See how your test quality improves over time

## 📜 License

MIT License - Because sharing is caring, and good test quality should be available to everyone.

## 🎯 Final Words

The Drill Sergeant doesn't exist to make your life harder. He exists to make your tests BETTER. 

Better tests = Better code = Better software = Better world.

**Now drop and give me 20 properly structured test cases!** 💪

---

*Made with ❤️ (and a healthy dose of sarcasm) by developers who care about test quality.*

**P.S.** - If you think this plugin is too strict, wait until you meet Production. The Drill Sergeant is just trying to prepare you for that harsh reality. 😈