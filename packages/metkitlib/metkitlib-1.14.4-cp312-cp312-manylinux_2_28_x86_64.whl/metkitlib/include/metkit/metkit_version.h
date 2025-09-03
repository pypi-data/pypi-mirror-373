#ifndef metkit_version_h
#define metkit_version_h

#define metkit_VERSION_STR "1.14.4"
#define metkit_VERSION     "1.14.4"

#define metkit_VERSION_MAJOR 1
#define metkit_VERSION_MINOR 14
#define metkit_VERSION_PATCH 4

#define metkit_GIT_SHA1 "f7e645d0f89c1f10aba00142c10d161c3e50d021"

#ifdef __cplusplus
extern "C" {
#endif

const char * metkit_version();

unsigned int metkit_version_int();

const char * metkit_version_str();

const char * metkit_git_sha1();

#ifdef __cplusplus
}
#endif


#endif // metkit_version_h
