def pipline(chat_ids: list[int], participant_types: list[str] | None = None) -> list[dict]:
    match_stage = {
        "chat_id": {"$in": chat_ids}
    }

    if participant_types:
        match_stage["type"] = {"$in": participant_types}

    return [
        {
            "$match": match_stage
        },
        {
            "$facet": {
                "active_participant_count": [
                    {
                        "$group": {
                            "_id": None,
                            "user_ids": {"$addToSet": "$user_id"}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "active_participant_count": {"$size": "$user_ids"}
                        }
                    }
                ],
                "participant_type_counts": [
                    {
                        "$group": {
                            "_id": "$type",
                            "count": {"$sum": 1}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "k": {"$toString": "$_id"},
                            "v": "$count"
                        }
                    },
                    {
                        "$sort": {"v": -1}
                    },
                    {
                        "$group": {
                            "_id": None,
                            "map": {"$push": {"k": "$k", "v": "$v"}}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "participant_type_counts": {"$arrayToObject": "$map"}
                        }
                    }
                ],
                "recommendation_counts": [
                    {
                        "$group": {
                            "_id": "$recommendation",
                            "count": {"$sum": 1}
                        }
                    },
                    {
                        "$sort": {"_id": -1}
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "k": {"$toString": "$_id"},
                            "v": "$count"}
                    },
                    {
                        "$group": {
                            "_id": None,
                            "map": {"$push": {"k": "$k", "v": "$v"}}
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "recommendation_counts": {"$arrayToObject": "$map"}
                        }
                    }
                ]
            }
        },
        {
            "$project": {
                "active_participant_count": {"$arrayElemAt": ["$active_participant_count.active_participant_count", 0]},
                "participant_type_counts": {"$arrayElemAt": ["$participant_type_counts.participant_type_counts", 0]},
                "recommendation_counts": {"$arrayElemAt": ["$recommendation_counts.recommendation_counts", 0]}
            }
        }
    ]

