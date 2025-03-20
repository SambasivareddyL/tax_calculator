import sys
import requests
import json

# Default IRS values for 2024 (update manually if IRS API is unavailable)
DEFAULT_STANDARD_DEDUCTION = {
    2023: 14600, 
    2024: 15000  
}
DEFAULT_HSA_LIMIT = {
    2023: 3850,   
    2024: 4150    
}
DEFAULT_401K_LIMIT = {
    2023: 22500,  
    2024: 23000  
}

def fetch_irs_limits(year):
    """
    Fetches IRS limits (Standard Deduction, HSA, 401K) from IRS API.
    Falls back to default values if the request fails.
    """
    try:
        url = f"https://www.irs.gov/tax-updates/{year}"  # Example URL, replace if IRS API is available
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        irs_data = response.json()

        return {
            "standard_deduction": irs_data.get("standard_deduction", DEFAULT_STANDARD_DEDUCTION.get(year, 15000)),
            "hsa_limit": irs_data.get("hsa_limit", DEFAULT_HSA_LIMIT.get(year, 4150)),
            "k401_limit": irs_data.get("k401_limit", DEFAULT_401K_LIMIT.get(year, 23000))
        }

    except Exception as e:
        print(f"⚠️ Warning: Failed to fetch IRS limits. Using defaults for {year}. ({e})")
        return {
            "standard_deduction": DEFAULT_STANDARD_DEDUCTION.get(year, 15000),
            "hsa_limit": DEFAULT_HSA_LIMIT.get(year, 4150),
            "k401_limit": DEFAULT_401K_LIMIT.get(year, 23000)
        }

def calculate_refund(wages, fed_withholding, hsa_contribution, k401_contribution, year):
    """
    Calculates tax refund or amount owed using IRS limits.
    """
    # Fetch IRS Limits
    irs_limits = fetch_irs_limits(year)
    standard_deduction = irs_limits["standard_deduction"]
    hsa_limit = irs_limits["hsa_limit"]
    k401_limit = irs_limits["k401_limit"]

    # Ensure HSA and 401K contributions are within legal limits
    hsa_contribution = min(hsa_contribution, hsa_limit)
    k401_contribution = min(k401_contribution, k401_limit)

    # Step 1: Adjusted Gross Income (AGI)
    pre_tax_deductions = hsa_contribution + k401_contribution
    agi = wages - pre_tax_deductions

    # Step 2: Taxable Income
    taxable_income = max(0, agi - standard_deduction)

    # Step 3: Calculate Federal Tax Owed (2023 & 2024 Single Filer Brackets)
    tax_brackets = {
        2023: [
            (11000, 0.10),
            (44725, 0.12),
            (95375, 0.22),
            (182100, 0.24),
            (231250, 0.32),
            (578125, 0.35),
            (float("inf"), 0.37)
        ],
        2024: [
            (11500, 0.10),
            (47150, 0.12),
            (100525, 0.22),
            (191950, 0.24),
            (243725, 0.32),
            (609350, 0.35),
            (float("inf"), 0.37)
        ]
    }

    tax_bracket = tax_brackets.get(year, tax_brackets[2024])
    tax_owed = 0
    previous_bracket = 0

    for bracket, rate in tax_bracket:
        if taxable_income > previous_bracket:
            taxable_at_this_rate = min(taxable_income, bracket) - previous_bracket
            tax_owed += taxable_at_this_rate * rate
        else:
            break
        previous_bracket = bracket

    # Step 4: Calculate Refund or Amount Owed
    refund_or_due = fed_withholding - tax_owed

    result = {
        "year": year,
        "agi": agi,
        "taxable_income": taxable_income,
        "standard_deduction": standard_deduction,
        "hsa_contribution": hsa_contribution,
        "k401_contribution": k401_contribution,
        "tax_owed": tax_owed,
        "refund_or_due": refund_or_due
    }

    with open('result.json', 'w') as f:
        json.dump(result, f, indent=4)

    # Output result
    print("\n--- Tax Calculation Summary ---")
    print(f"Filing Year: {year}")
    print(f"Adjusted Gross Income (AGI): ${agi:,.2f}")
    print(f"Taxable Income: ${taxable_income:,.2f}")
    print(f"Standard Deduction: ${standard_deduction:,.2f}")
    print(f"HSA Contribution (Capped at ${hsa_limit}): ${hsa_contribution:,.2f}")
    print(f"401(k) Contribution (Capped at ${k401_limit}): ${k401_contribution:,.2f}")
    print(f"Federal Tax Owed: ${tax_owed:,.2f}")

    if refund_or_due > 0:
        print(f"🎉 You will receive a refund of ${refund_or_due:,.2f}")
    else:
        print(f"💰 You owe ${abs(refund_or_due):.2f} to the IRS")

def main():
    """
    Main function to take user input and calculate refund.
    """
    if len(sys.argv) != 6:
        print("Usage: python tax_calculator.py <wages> <fed_withholding> <hsa_contribution> <k401_contribution> <year>")
        sys.exit(1)

    try:
        wages = float(sys.argv[1])
        fed_withholding = float(sys.argv[2])
        hsa_contribution = float(sys.argv[3])
        k401_contribution = float(sys.argv[4])
        year = int(sys.argv[5])

        if year not in [2023, 2024]:
            print("⚠️ Only 2023 and 2024 tax years are supported.")
            sys.exit(1)

        calculate_refund(wages, fed_withholding, hsa_contribution, k401_contribution, year)

    except ValueError:
        print("Error: Please enter valid numeric values for wages, withholding, HSA, 401(k), and year.")
        sys.exit(1)

if __name__ == "__main__":
    main()
