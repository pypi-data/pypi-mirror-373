"""
Custom exceptions for subtitle_utils library.

이 모듈은 자막 처리 과정에서 발생할 수 있는 다양한 예외상황을
명확하게 구분하여 처리하기 위한 커스텀 예외 클래스들을 정의합니다.
"""


class SubtitleError(Exception):
    """
    자막 라이브러리의 기본 예외 클래스.

    모든 subtitle_utils 관련 예외의 부모 클래스로,
    라이브러리에서 발생하는 일반적인 오류를 나타냅니다.
    """

    pass


class SubtitleParseError(SubtitleError):
    """
    자막 파일 파싱 중 발생하는 예외.

    자막 파일의 형식이 올바르지 않거나 파싱 과정에서
    오류가 발생했을 때 발생하는 예외입니다.

    Examples:
        - 잘못된 시간 형식
        - 예상하지 못한 파일 구조
        - 인코딩 문제
    """

    pass


class SubtitleFileError(SubtitleError):
    """
    파일 입출력 관련 예외.

    자막 파일을 읽거나 쓰는 과정에서 발생하는
    파일 시스템 관련 오류를 나타냅니다.

    Examples:
        - 파일이 존재하지 않음
        - 파일 권한 문제
        - 디스크 용량 부족
    """

    pass
