def pipeline(chat_ids: list[int], participant_types: list[str]) -> list[dict]:
    return [
        {
            "$match": {
                "chat_id": {"$in": chat_ids},
                "type": {"$in": participant_types}
            }
        },
        {
            "$group": {
                "_id": "$chat_name",
                "user_analysis": {"$push": "$$ROOT"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "chat_name": "$_id",
                "user_analysis": {
                    "$sortArray": {
                        "input": "$user_analysis",
                        "sortBy": {
                            "type": 1,
                            "recommendation": -1,
                            "impact": -1
                        }
                    }
                }
            }
        }
    ]

