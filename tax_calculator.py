import sys

def calculate_tax(taxable_income):
    # Example tax brackets for the US (2025)
    brackets = [
        (9950, 0.10),
        (40525, 0.12),
        (86375, 0.22),
        (164925, 0.24),
        (209425, 0.32),
        (523600, 0.35),
        (float('inf'), 0.37),
    ]

    tax = 0
    previous_bracket_limit = 0

    for bracket_limit, rate in brackets:
        if taxable_income <= bracket_limit:
            tax += (taxable_income - previous_bracket_limit) * rate
            break
        else:
            tax += (bracket_limit - previous_bracket_limit) * rate
            previous_bracket_limit = bracket_limit

    return tax

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python calculate_tax.py <taxable_income>")
        sys.exit(1)

    taxable_income = float(sys.argv[1])
    tax = calculate_tax(taxable_income)
    with open('tax_output.txt', 'w') as f:
        f.write(str(tax))
    print(f"Tax calculated: {tax}")