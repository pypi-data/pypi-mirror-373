# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/inductive-logic-programming/workflows/CI/badge.svg)](https://github.com/benedictchen/inductive-logic-programming/actions)
[![PyPI version](https://badge.fury.io/py/inductive-logic-programming.svg)](https://badge.fury.io/py/inductive-logic-programming)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Inductive Logic Programming

🔍 Learning from examples

**Muggleton, S. (1991) - "Inductive logic programming"**

## 📦 Installation

```bash
pip install inductive-logic-programming
```

## 🚀 Quick Start

```python
import inductive_logic_programming

# Create training examples
examples = [
    inductive_logic_programming.Example("parent(tom, bob)", True),
    inductive_logic_programming.Example("parent(bob, ann)", True), 
    inductive_logic_programming.Example("parent(tom, liz)", True),
    inductive_logic_programming.Example("parent(bob, pat)", True),
    inductive_logic_programming.Example("parent(pat, jim)", True),
    inductive_logic_programming.Example("grandparent(tom, ann)", True),
    inductive_logic_programming.Example("grandparent(tom, pat)", True),
]

# Use FOIL learner to discover rules
foil = inductive_logic_programming.FOILLearner()
learned_rules = foil.learn(examples)

print("✅ Learned rules:")
for rule in learned_rules:
    print(f"   {rule}")

# Alternative: Use Progol system
progol = inductive_logic_programming.ProgolSystem()
progol.set_examples(examples)
hypothesis = progol.learn()
print(f"✅ Progol hypothesis: {hypothesis}")
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Muggleton, S. (1991) - "Inductive logic programming"
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**