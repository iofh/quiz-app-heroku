import datetime
from rest_framework import serializers
from .models import Tournament, CATEGORY_CHOICE, DIFFICULTY_CHOICE, Question

class TournamentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tournament
        fields = ['id','name', 'category', 'difficulty', 'start_date', 'end_date']

    def validate(self, data):
        """
        Check that the start is before the stop.
        """
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("finish must occur after start")
        if datetime.date.today() > data['end_date']:
            raise serializers.ValidationError("End date must occur after today")
        return data