"""
SRTHandler 클래스에 대한 단위 테스트.

이 테스트 모듈은 SRTHandler의 모든 주요 기능을 검증합니다:
- 파일 로드/저장
- 자막 항목 추가/조회
- 에러 처리
"""

import pytest
from pathlib import Path
import tempfile
import os

from subtitle_utils import SRTHandler
from subtitle_utils.exceptions import SubtitleFileError, SubtitleParseError


class TestSRTHandler:
    """SRTHandler 클래스의 테스트 케이스들."""

    @pytest.fixture
    def sample_srt_content(self):
        """테스트용 SRT 파일 내용."""
        return """1
00:00:01,000 --> 00:00:03,000
첫 번째 자막입니다.

2
00:00:04,000 --> 00:00:06,000
두 번째 자막입니다.

3
00:00:07,000 --> 00:00:10,000
세 번째 자막입니다.
"""

    @pytest.fixture
    def temp_srt_file(self, sample_srt_content):
        """임시 SRT 파일을 생성하는 픽스처."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".srt", delete=False, encoding="utf-8"
        ) as f:
            f.write(sample_srt_content)
            temp_path = f.name

        yield temp_path

        # 테스트 후 임시 파일 정리
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_init_empty(self):
        """빈 SRTHandler 초기화 테스트."""
        handler = SRTHandler()
        assert handler.file_path is None
        assert len(handler) == 0

    def test_init_with_file(self, temp_srt_file):
        """파일과 함께 SRTHandler 초기화 테스트."""
        handler = SRTHandler(temp_srt_file)
        assert handler.file_path == Path(temp_srt_file)
        assert len(handler) == 3

    def test_load_valid_file(self, temp_srt_file):
        """유효한 파일 로드 테스트."""
        handler = SRTHandler()
        handler.load(temp_srt_file)

        assert len(handler) == 3
        assert handler.file_path == Path(temp_srt_file)

        # 첫 번째 자막 확인
        first_subtitle = handler.get_subtitle(0)
        assert first_subtitle is not None
        assert "첫 번째 자막" in first_subtitle.content

    def test_load_nonexistent_file(self):
        """존재하지 않는 파일 로드 테스트."""
        handler = SRTHandler()

        with pytest.raises(SubtitleFileError) as exc_info:
            handler.load("nonexistent_file.srt")

        assert "파일을 찾을 수 없습니다" in str(exc_info.value)

    def test_load_directory_instead_of_file(self, tmp_path):
        """디렉토리를 파일로 로드하려는 경우 테스트."""
        handler = SRTHandler()

        with pytest.raises(SubtitleFileError) as exc_info:
            handler.load(tmp_path)

        assert "지정된 경로가 파일이 아닙니다" in str(exc_info.value)

    def test_save_to_new_file(self, temp_srt_file, tmp_path):
        """새 파일로 저장 테스트."""
        handler = SRTHandler(temp_srt_file)
        new_file_path = tmp_path / "output.srt"

        handler.save(new_file_path)

        assert new_file_path.exists()
        assert handler.file_path == new_file_path

        # 저장된 파일을 다시 로드하여 확인
        new_handler = SRTHandler(new_file_path)
        assert len(new_handler) == 3

    def test_save_without_path(self):
        """경로 지정 없이 저장 시도 테스트."""
        handler = SRTHandler()

        with pytest.raises(Exception):  # SubtitleError 또는 다른 에러
            handler.save()

    def test_add_subtitle(self):
        """자막 항목 추가 테스트."""
        handler = SRTHandler()

        handler.add_subtitle("00:00:01,000", "00:00:03,000", "새로운 자막")

        assert len(handler) == 1
        subtitle = handler.get_subtitle(0)
        assert subtitle is not None
        assert subtitle.content == "새로운 자막"

    def test_add_subtitle_invalid_time_format(self):
        """잘못된 시간 형식으로 자막 추가 테스트."""
        handler = SRTHandler()

        with pytest.raises(SubtitleParseError):
            handler.add_subtitle("invalid_time", "00:00:03,000", "텍스트")

    def test_get_subtitle_valid_index(self, temp_srt_file):
        """유효한 인덱스로 자막 조회 테스트."""
        handler = SRTHandler(temp_srt_file)

        subtitle = handler.get_subtitle(1)  # 두 번째 자막
        assert subtitle is not None
        assert "두 번째 자막" in subtitle.content

    def test_get_subtitle_invalid_index(self, temp_srt_file):
        """유효하지 않은 인덱스로 자막 조회 테스트."""
        handler = SRTHandler(temp_srt_file)

        subtitle = handler.get_subtitle(999)
        assert subtitle is None

    def test_get_subtitle_count(self, temp_srt_file):
        """자막 개수 조회 테스트."""
        handler = SRTHandler(temp_srt_file)

        assert handler.get_subtitle_count() == 3
        assert len(handler) == 3  # __len__ 메서드 테스트

    def test_get_duration(self, temp_srt_file):
        """전체 자막 길이 조회 테스트."""
        handler = SRTHandler(temp_srt_file)

        duration = handler.get_duration()
        assert duration is not None
        # 마지막 자막의 종료시간이 00:00:10,000 이어야 함

    def test_get_duration_empty(self):
        """빈 자막에서 길이 조회 테스트."""
        handler = SRTHandler()

        duration = handler.get_duration()
        assert duration is None

    def test_iteration(self, temp_srt_file):
        """반복자 기능 테스트."""
        handler = SRTHandler(temp_srt_file)

        subtitle_texts = []
        for subtitle in handler:
            subtitle_texts.append(subtitle.content)

        assert len(subtitle_texts) == 3
        assert "첫 번째 자막" in subtitle_texts[0]

    def test_indexing(self, temp_srt_file):
        """인덱스 접근 테스트."""
        handler = SRTHandler(temp_srt_file)

        subtitle = handler[0]  # __getitem__ 메서드 테스트
        assert "첫 번째 자막" in subtitle.content

        with pytest.raises(IndexError):
            _ = handler[999]
