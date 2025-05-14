from collections import defaultdict
from operator import attrgetter

from cachetools import TTLCache, cachedmethod
from pymongo.synchronous.database import Database

from telegram.model.analysis_result import UserGeneralAnalysisResult, UserAnalysisResult, ChatsAnalysisResult, \
    ChatAnalysisResult
from telegram.model.user_analysis_entity import TelegramUserAnalysisEntity
from telegram.repo.chat_repository import TelegramChatRepository
from telegram.repo.pipelines import analyze_chats, analyze_each_chat, group_user_analysis_by_chat


class TelegramChatAnalyzer:
    def __init__(self, database: Database, cache: TTLCache, chat_repository: TelegramChatRepository):
        self._database = database
        self._cache = cache
        self._chat_repository = chat_repository
        self.RECOMMENDATION_COUNT_PIPLINE = 'recommendation_count'
        self.PARTICIPANT_TYPES_PIPLINE = 'participant_types'
        self.ACTIVE_PARTICIPANTS_PIPLINE = 'active_participants'

    def analyze_chats(self, chat_ids: list[int], participant_types: list[str] = None) -> ChatsAnalysisResult:
        users_analysis_collection = self._database[str(chat_ids[0]) if len(chat_ids) == 1 else 'all']
        pipline = analyze_chats.pipline(
            chat_ids=chat_ids,
            participant_types=participant_types
        )
        result = list(users_analysis_collection.aggregate(pipline))
        chats = self._chat_repository.find_by_ids(chat_ids)

        return ChatsAnalysisResult(
            titles=list(chat.title for chat in chats),
            total_participant_count=sum(chat.participant_count for chat in chats),
            **result[0],
            participant_types=participant_types
        )

    def analyze_chats_detailed(self, chat_ids: list[int], participant_types: list[str] | None = None) -> list[
        ChatAnalysisResult]:
        users_analysis_collection = self._database[str(chat_ids[0]) if len(chat_ids) == 1 else 'all']
        pipline = analyze_each_chat.pipline(
            chat_ids=chat_ids,
            participant_types=participant_types
        )
        result = list(users_analysis_collection.aggregate(pipline))
        id_to_chat_dict = self._chat_repository.get_id_to_chat_dict(chat_ids)

        return [
            ChatAnalysisResult(
                **vars(id_to_chat_dict[doc['chat_id']]),
                **doc,
                participant_types=participant_types
            )
            for doc in result
        ]

    def analyze_user(self, user_id: int) -> UserGeneralAnalysisResult:
        all_users_analysis_collection = self._database['all']
        result = list(all_users_analysis_collection.find({'user_id': user_id}))

        total_message_count = 0
        message_count_by_participant_type = defaultdict(int)
        total_explanation: dict[str, int] = defaultdict(int)
        chat_ids: list[int] = []
        total_weighted_impact = 0
        total_weighted_recommendation = 0

        for document in result:
            message_count = document['explanation']['total']

            for message_type, count in document['explanation'].items():
                if not isinstance(count, int):
                    continue
                total_explanation[message_type] += count

            chat_ids.append(document['chat_id'])
            participant_type = document['type']
            impact_score = document['impact']
            recommendation_score = document['recommendation']

            total_message_count += message_count
            message_count_by_participant_type[participant_type] += message_count
            total_weighted_impact += impact_score * message_count
            total_weighted_recommendation += recommendation_score * message_count

        chats = self._chat_repository.find_all()
        participant_chats = list(filter(lambda chat: chat.telegram_id in chat_ids, chats))

        participant_type_percentages = dict(
            sorted(
                (
                    (participant_type, round((count / total_message_count) * 100, 2))
                    for participant_type, count in message_count_by_participant_type.items()
                ),
                key=lambda item: item[1],
                reverse=True
            )
        )

        return UserGeneralAnalysisResult(
            chat_titles=list(map(lambda chat: chat.title, participant_chats)),
            participant_to_all_chats=(len(participant_chats), len(chats)),
            average_impact=round(total_weighted_impact / total_message_count, 1) if total_message_count else 0,
            average_recommendation=round(
                total_weighted_recommendation / total_message_count) if total_message_count else 0,
            participant_type_percentages=participant_type_percentages,
            explanation=total_explanation
        )

    def analyze_user_detailed(self, user_id: int) -> list[UserAnalysisResult]:
        all_users_analysis_collection = self._database['all']
        documents = list(all_users_analysis_collection.find({'user_id': user_id}))

        return [
            UserAnalysisResult(
                chat_title=document['chat_name'],
                participant_type=document['type'],
                impact=document['impact'],
                recommendation=document['recommendation'],
                explanation=document['explanation']
            )
            for document in documents
        ]

    def get_user_analysis_group_by_chat_title(self, chat_ids: list[int], participant_types: list[str]) -> dict[str, list[TelegramUserAnalysisEntity]]:
        all_users_analysis_collection = self._database['all']
        pipline = group_user_analysis_by_chat.pipeline(
            chat_ids=chat_ids,
            participant_types=participant_types
        )
        result = list(all_users_analysis_collection.aggregate(pipline))
        chat_title_to_user_analysis: dict[str, list[TelegramUserAnalysisEntity]] = {}
        for document in result:
            chat_title_to_user_analysis[document['chat_name']] = [
                TelegramUserAnalysisEntity.from_document(user_analysis_document)
                for user_analysis_document in document['user_analysis']
            ]
        return chat_title_to_user_analysis

    def has_analysis_for_user(self, user_id: int) -> bool:
        all_users_analysis_collection = self._database['all']
        return all_users_analysis_collection.find_one({'user_id': user_id}) is not None

    @cachedmethod(attrgetter('_cache'), key=lambda *_: 'user_types')
    def get_distinct_user_types(self) -> list[str]:
        return self._database['all'].distinct('type')
