from ..core import tool

@tool
def calculate_compound_interest(principal: float, rate: float, years: int, compounds_per_year: int = 1):
    """
    Calculates the future value of an investment with compound interest.
    Use this for precise financial calculations involving interest.

    Args:
        principal: The initial principal amount (e.g., 1000).
        rate: The annual interest rate as a decimal (e.g., 0.05 for 5%).
        years: The number of years the money is invested for.
        compounds_per_year: The number of times that interest is compounded per year (default is 1 for annually).
    """
    if principal < 0 or rate < 0 or years < 0 or compounds_per_year <= 0:
        return {"error": "All financial inputs must be positive numbers."}

    # The formula for compound interest: A = P(1 + r/n)^(nt)
    amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
    
    total_interest = amount - principal

    return {
        "initial_principal": f"${principal:,.2f}",
        "future_value": f"${amount:,.2f}",
        "total_interest_earned": f"${total_interest:,.2f}",
        "years": years
    }
