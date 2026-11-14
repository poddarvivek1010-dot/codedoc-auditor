def calculate_health_score(findings):
    score = 100
    score -= len(findings["secrets"]) * 40
    score -= len(findings["todos"]) * 5
    if not findings["has_readme"]:
        score -= 15
    return max(0, score)
