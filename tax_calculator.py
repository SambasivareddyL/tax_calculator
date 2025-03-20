def calculate_refund():
    # User inputs
    wages = float(input("Enter your Wages, Tips, and Compensation: "))
    fed_withholding = float(input("Enter your Federal Withholding: "))
    hsa_contribution = float(input("Enter your HSA Contributions: "))
    k401_contribution = float(input("Enter your 401K Contributions: "))
    standard_deduction = float(input("Enter your Standard Deduction: "))

    # Step 1: Adjusted Gross Income (AGI)
    pre_tax_deductions = hsa_contribution + k401_contribution
    agi = wages - pre_tax_deductions

    # Step 2: Calculate Taxable Income
    taxable_income = max(0, agi - standard_deduction)

    # Step 3: Calculate Federal Income Tax (2023 Single Filer Brackets)
    tax_brackets = [
        (11000, 0.10),
        (33725, 0.12),
        (50650, 0.22),
        (43875, 0.24),
        (78525, 0.32),
        (46250, 0.35),
        (float("inf"), 0.37)
    ]

    tax_owed = 0
    remaining_income = taxable_income
    lower_limit = 0

    for bracket, rate in tax_brackets:
        if remaining_income > 0:
            taxable_amount = min(remaining_income, bracket)
            tax_owed += taxable_amount * rate
            remaining_income -= taxable_amount
        else:
            break

    # Step 4: Calculate Refund or Amount Owed
    refund_or_due = fed_withholding - tax_owed

    # Output result
    if refund_or_due > 0:
        print(f"You will receive a refund of ${refund_or_due:.2f}")
    else:
        print(f"You owe ${abs(refund_or_due):.2f} to the IRS")

# Run the function
if __name__ == "__main__":
    calculate_refund()
