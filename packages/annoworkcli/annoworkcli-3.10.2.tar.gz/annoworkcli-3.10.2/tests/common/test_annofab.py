from annoworkcli.common.annofab import get_annofab_project_id_from_job


class Test_get_annofab_project_id_from_job:
    def test_url(self):
        job = {
            "job_id": "foo",
            "external_linkage_info": {"url": "https://annofab.com/projects/bar"},
        }
        actual = get_annofab_project_id_from_job(job)
        excepted = "bar"
        assert actual == excepted

    def test_url_with_trailing_slash(self):
        job = {
            "job_id": "foo",
            "external_linkage_info": {"url": "https://annofab.com/projects/bar/"},
        }
        actual = get_annofab_project_id_from_job(job)
        excepted = "bar"
        assert actual == excepted

    def test_url_none(self):
        job = {
            "job_id": "foo",
            "external_linkage_info": {},
        }
        actual = get_annofab_project_id_from_job(job)
        assert actual is None
