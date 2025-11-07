@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem
@rem SPDX-License-Identifier: Apache-2.0
@rem

@if "%DEBUG%"=="" @echo off
@rem ##########################################################################
@rem
@rem  sparql-translator-complex-alignment startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.
@rem This is normally unused
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%..

@rem Resolve any "." and ".." in APP_HOME to make it shorter.
for %%i in ("%APP_HOME%") do set APP_HOME=%%~fi

@rem Add default JVM options here. You can also use JAVA_OPTS and SPARQL_TRANSLATOR_COMPLEX_ALIGNMENT_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS=

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% equ 0 goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH. 1>&2
echo. 1>&2
echo Please set the JAVA_HOME variable in your environment to match the 1>&2
echo location of your Java installation. 1>&2

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME% 1>&2
echo. 1>&2
echo Please set the JAVA_HOME variable in your environment to match the 1>&2
echo location of your Java installation. 1>&2

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\lib\sparql-translator-complex-alignment.jar;%APP_HOME%\lib\jena-arq-4.10.0.jar;%APP_HOME%\lib\gson-2.10.1.jar;%APP_HOME%\lib\slf4j-simple-2.0.9.jar;%APP_HOME%\lib\jena-core-4.10.0.jar;%APP_HOME%\lib\jsonld-java-0.13.4.jar;%APP_HOME%\lib\httpclient-cache-4.5.14.jar;%APP_HOME%\lib\httpclient-4.5.14.jar;%APP_HOME%\lib\jcl-over-slf4j-1.7.36.jar;%APP_HOME%\lib\jackson-annotations-2.15.3.jar;%APP_HOME%\lib\jackson-databind-2.15.3.jar;%APP_HOME%\lib\jackson-core-2.15.3.jar;%APP_HOME%\lib\titanium-json-ld-1.3.2.jar;%APP_HOME%\lib\jakarta.json-2.0.1.jar;%APP_HOME%\lib\protobuf-java-3.24.3.jar;%APP_HOME%\lib\libthrift-0.19.0.jar;%APP_HOME%\lib\jena-base-4.10.0.jar;%APP_HOME%\lib\commons-lang3-3.13.0.jar;%APP_HOME%\lib\slf4j-api-2.0.9.jar;%APP_HOME%\lib\jena-iri-4.10.0.jar;%APP_HOME%\lib\commons-cli-1.5.0.jar;%APP_HOME%\lib\RoaringBitmap-1.0.0.jar;%APP_HOME%\lib\httpcore-4.4.16.jar;%APP_HOME%\lib\commons-csv-1.10.0.jar;%APP_HOME%\lib\commons-io-2.14.0.jar;%APP_HOME%\lib\commons-codec-1.16.0.jar;%APP_HOME%\lib\commons-compress-1.24.0.jar;%APP_HOME%\lib\commons-collections4-4.4.jar;%APP_HOME%\lib\caffeine-3.1.8.jar;%APP_HOME%\lib\collection-0.7.jar;%APP_HOME%\lib\checker-qual-3.37.0.jar;%APP_HOME%\lib\error_prone_annotations-2.21.1.jar


@rem Execute sparql-translator-complex-alignment
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %SPARQL_TRANSLATOR_COMPLEX_ALIGNMENT_OPTS%  -classpath "%CLASSPATH%" sparql_parser_java.SparqlAstParser %*

:end
@rem End local scope for the variables with windows NT shell
if %ERRORLEVEL% equ 0 goto mainEnd

:fail
rem Set variable SPARQL_TRANSLATOR_COMPLEX_ALIGNMENT_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
set EXIT_CODE=%ERRORLEVEL%
if %EXIT_CODE% equ 0 set EXIT_CODE=1
if not ""=="%SPARQL_TRANSLATOR_COMPLEX_ALIGNMENT_EXIT_CONSOLE%" exit %EXIT_CODE%
exit /b %EXIT_CODE%

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
