# PEP 386
# X: 주요(Major) 버전 (큰 변화나 호환성 깨짐)
# Y: 부(Minor) 버전 (기능 추가, 호환성 유지)
# Z: 패치(Patch) 버전 (버그 수정)
VERSION = (1, 1, 0)
__version__ = ".".join([str(x) for x in VERSION])
__all__ = ["aws",]