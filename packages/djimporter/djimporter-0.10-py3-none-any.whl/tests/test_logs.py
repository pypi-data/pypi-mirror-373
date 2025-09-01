"""
This tests is a collection of test for check the model and views logs
"""
from django.test import TestCase
from django.urls import reverse

from djimporter.models import ImportLog


class TestLogs(TestCase):

    def setUp(self):
        self.log_id = 1
        data = {'id': self.log_id, 'status': ImportLog.CREATED, 'user': "user1",
                'input_file': "File_one.csv"}
        self.log = ImportLog.objects.create(**data)

    def test_entrylogs_list(self):
        url = reverse('djimporter:importlog-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_entrylog_id(self):
        url = reverse('djimporter:importlog-detail', args=[self.log_id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_entrylog_delete_get(self):
        url = reverse('djimporter:importlog-delete', args=[self.log_id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_entrylog_delete_post(self):
        self.assertTrue(ImportLog.objects.filter(id=self.log_id).exists())
        url = reverse('djimporter:importlog-delete', args=[self.log_id])
        res = self.client.post(url)
        self.assertEqual(res.status_code, 302)
        self.assertFalse(ImportLog.objects.filter(id=self.log_id).exists())
