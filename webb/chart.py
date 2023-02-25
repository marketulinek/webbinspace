from django.http import JsonResponse


class WrongTypeChart(Exception):
    pass


class Chart:

    def __init__(self, chart_type, data_labels, dataset_label, dataset_data):
        self.type = chart_type
        self.allowed_types = ['bar']

        self.data_labels = data_labels
        self.dataset_label = dataset_label
        self.dataset_data = dataset_data
        self.tooltip_label = None
        self.options = None

        self.backgroundColor = 'rgba(255, 193, 7, 0.1)'
        self.borderColor = 'rgba(255, 193, 7, 1)'
        self.borderWidth = 1

    def create_json(self):
        self.check_type()

        config = {
            'type': self.type,
            'data': {
                'labels': self.data_labels,
                'datasets': [{
                    'label': self.dataset_label,
                    'data': self.dataset_data,
                    'borderWidth': self.borderWidth,
                    'backgroundColor': self.backgroundColor,
                    'borderColor': self.borderColor
                }]
            }
        }

        if self.options:
            config['options'] = self.options

        if self.tooltip_label:
            config['tooltips'] = self.tooltip_label

        return JsonResponse(config)

    def check_type(self):
        if self.type not in self.allowed_types:
            message = f"Allowed types: {', '.join(self.allowed_types)}."
            raise WrongTypeChart(message)


class TimeSpentObservingChart(Chart):

    def __init__(self, data_labels, dataset_data, tooltip_label):

        dataset_label = 'The time spent in days, hours'
        super().__init__('line', data_labels, dataset_label, dataset_data)

        self.tooltip_label = tooltip_label
        self.options = {
            'indexAxis': 'y',
            'responsive': 'true',
            'plugins': {
                'tooltip': {
                    'displayColors': 'false'
                }
            }
        }
