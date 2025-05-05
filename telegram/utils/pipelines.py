def distinct_count_pipeline(field_name: str) -> list[dict]:
    return [
        {
            "$group": {
                "_id": f"${field_name}"
            }
        },
        {
            "$count": "distinct_count"
        }
    ]


def total_sum_pipeline(field_name: str) -> list[dict]:
    return [
        {
            "$group": {
                "_id": None,
                "total_sum": {"$sum": f"${field_name}"}
            }
        }
    ]


def count_by_group_pipeline(field_name: str) -> list[dict]:
    return [
        {
            "$group": {
                "_id": f"${field_name}",
                "count": {"$sum": 1}
            }
        }
    ]


def group_by_field_with_name_pipeline(group_field: str, field_name: str) -> list[dict]:
    return [
        {
            "$group": {
                "_id": f"${group_field}",
                "name": {"$first": f"${field_name}"}
            }
        }
    ]
