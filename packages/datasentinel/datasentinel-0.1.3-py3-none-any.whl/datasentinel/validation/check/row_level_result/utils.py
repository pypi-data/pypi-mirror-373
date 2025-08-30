def evaluate_pass_rate(total_rows: int, bad_records: int) -> float:
    try:
        return 1 - (bad_records / total_rows)
    except ZeroDivisionError:
        return 1.0


def are_id_columns_in_rule_columns(id_columns: list[str], rule_columns: str | list[str]) -> bool:
    rule_columns = [rule_columns] if isinstance(rule_columns, str) else rule_columns
    return bool({item.lower() for item in id_columns} & {item.lower() for item in rule_columns})
