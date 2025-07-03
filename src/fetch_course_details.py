from typing import List
import aiohttp
import asyncio

# Returns a list of paths for each course (typically just a list with one path, but some courses have several paths within the same curriculum)
# Path elemens are the names of curriculum tree nodes leading to that course
async def fetch_curriculum_paths(session: aiohttp.ClientSession, course_id, curriculum_id) -> List[List[str]]:
   response = await session.get(f"https://campus.tum.de/tumonline/ee/rest/slc.cm.curriculumposition/positions/{course_id}/course/allCurriculumPositions")
   responseJson = await response.json()
   matching_curriculums = [curriculumDto for curriculumDto in responseJson["resource"]
                           if str(curriculumDto["content"]["coCurriculumPositionDto"]["studyNameInfoDto"]["curriculumVersionId"]) == str(curriculum_id)]

   def extract_translation(name_dto, language_code):
       (translation_dto,) = [translation_dto for translation_dto in name_dto["translations"]["translation"] if translation_dto["lang"] == language_code]
       print(name_dto, translation_dto)
       return translation_dto.get("value") or name_dto["value"]

   paths = [[
         extract_translation(curriculum_path_element["name"], language_code="en")
         for curriculum_path_element in matching_curriculum["content"]["coCurriculumPositionDto"]["curriculumPositionPathDto"]["path"]
      ] for matching_curriculum in matching_curriculums
   ]
   return paths

async def fetch_related_courses(course_ids):
    pass
#     https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses/same-courses/950802917

#     {
#    "links" : [ {
#       "rel" : "related",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#       "name" : "IdentityLibDto",
#       "key" : "11582B8747F1A812"
#    }, {
#       "rel" : "related",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/4B42C6F2D2C7853F",
#       "name" : "IdentityLibDto",
#       "key" : "4B42C6F2D2C7853F"
#    }, {
#       "rel" : "related",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#       "name" : "IdentityLibDto",
#       "key" : "11582B8747F1A812"
#    }, {
#       "rel" : "related",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/FEA24C51FE8ADBAA",
#       "name" : "IdentityLibDto",
#       "key" : "FEA24C51FE8ADBAA"
#    }, {
#       "rel" : "detail",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses/950734482",
#       "name" : "CpCourseDto",
#       "key" : "950734482"
#    }, {
#       "rel" : "related",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#       "name" : "IdentityLibDto",
#       "key" : "11582B8747F1A812"
#    }, {
#       "rel" : "related",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#       "name" : "IdentityLibDto",
#       "key" : "11582B8747F1A812"
#    }, {
#       "rel" : "detail",
#       "href" : "https://campus.tum.de/tumonline/ee/rest/slc.tm.cp/student/courses/950691822",
#       "name" : "CpCourseDto",
#       "key" : "950691822"
#    } ],
#    "courses" : [ {
#       "id" : 950734482,
#       "courseNumber" : {
#          "dotIndex" : 0,
#          "databaseValue" : "0000002558",
#          "courseNumber" : "0000002558"
#       },
#       "semesterDto" : {
#          "id" : 200,
#          "key" : "24S",
#          "academicYearId" : 1617,
#          "semesterType" : "S",
#          "semesterDesignation" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "Summer semester 2024",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "Sommersemester 2024"
#                }, {
#                   "lang" : "en",
#                   "value" : "Summer semester 2024"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "startOfAcademicSemester" : {
#             "coType" : "date",
#             "value" : "2024-04-01"
#          },
#          "endOfAcademicSemester" : {
#             "coType" : "date",
#             "value" : "2024-09-30"
#          },
#          "shortName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "2024 S",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "2024 S"
#                }, {
#                   "lang" : "en"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          }
#       },
#       "courseTitle" : {
#          "coType" : "model-core.lib.model.langdata",
#          "value" : "Causal Inference in Time series (CIT4230006)",
#          "translations" : {
#             "translation" : [ {
#                "lang" : "de",
#                "value" : "Causal Inference in Time Series (CIT4230006)"
#             }, {
#                "lang" : "en",
#                "value" : "Causal Inference in Time series (CIT4230006)"
#             }, {
#                "lang" : "fr"
#             }, {
#                "lang" : "it"
#             } ]
#          }
#       },
#       "courseTypeDto" : {
#          "id" : 17,
#          "key" : "VO",
#          "courseTypeName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "lecture",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "Vorlesung"
#                }, {
#                   "lang" : "en",
#                   "value" : "lecture"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "courseTypeShortName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "VO",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "VO"
#                }, {
#                   "lang" : "en",
#                   "value" : "VO"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "sort" : 10
#       },
#       "lectureships" : [ {
#          "id" : 10328901,
#          "courseId" : 950734482,
#          "identityLibDto" : {
#             "id" : 385410,
#             "personId" : 385410,
#             "obfuscated" : "11582B8747F1A812",
#             "firstName" : "Seyed Jalal",
#             "lastName" : "Etesami",
#             "gender" : "MALE",
#             "genderNrForTitle" : 1,
#             "businessCardLink" : {
#                "rel" : "related",
#                "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#                "name" : "IdentityLibDto",
#                "key" : "11582B8747F1A812"
#             }
#          },
#          "teachingFunction" : {
#             "id" : 1,
#             "key" : "L",
#             "name" : "Leiter*in"
#          }
#       }, {
#          "id" : 10348987,
#          "courseId" : 950734482,
#          "identityLibDto" : {
#             "id" : 389720,
#             "personId" : 389720,
#             "obfuscated" : "4B42C6F2D2C7853F",
#             "firstName" : "Yutong",
#             "lastName" : "Chao",
#             "gender" : "MALE",
#             "genderNrForTitle" : 1,
#             "businessCardLink" : {
#                "rel" : "related",
#                "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/4B42C6F2D2C7853F",
#                "name" : "IdentityLibDto",
#                "key" : "4B42C6F2D2C7853F"
#             }
#          },
#          "teachingFunction" : {
#             "id" : 2,
#             "key" : "V",
#             "name" : "Vortragende*r"
#          }
#       }, {
#          "id" : 10328902,
#          "courseId" : 950734482,
#          "identityLibDto" : {
#             "id" : 385410,
#             "personId" : 385410,
#             "obfuscated" : "11582B8747F1A812",
#             "firstName" : "Seyed Jalal",
#             "lastName" : "Etesami",
#             "gender" : "MALE",
#             "genderNrForTitle" : 1,
#             "businessCardLink" : {
#                "rel" : "related",
#                "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#                "name" : "IdentityLibDto",
#                "key" : "11582B8747F1A812"
#             }
#          },
#          "teachingFunction" : {
#             "id" : 2,
#             "key" : "V",
#             "name" : "Vortragende*r"
#          }
#       }, {
#          "id" : 10349884,
#          "courseId" : 950734482,
#          "identityLibDto" : {
#             "id" : 370484,
#             "personId" : 370484,
#             "obfuscated" : "FEA24C51FE8ADBAA",
#             "firstName" : "Larkin",
#             "lastName" : "Liu",
#             "gender" : "MALE",
#             "genderNrForTitle" : 1,
#             "businessCardLink" : {
#                "rel" : "related",
#                "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/FEA24C51FE8ADBAA",
#                "name" : "IdentityLibDto",
#                "key" : "FEA24C51FE8ADBAA"
#             }
#          },
#          "teachingFunction" : {
#             "id" : 2,
#             "key" : "V",
#             "name" : "Vortragende*r"
#          }
#       } ],
#       "displayMoreLectureships" : false,
#       "displayCourseRegistrationInfo" : false,
#       "courseNormConfigs" : [ {
#          "key" : "SST",
#          "shortName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "SWS",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "SWS"
#                }, {
#                   "lang" : "en",
#                   "value" : "SWS"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "name" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "Semester weekly hours",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "Semesterwochenstunden"
#                }, {
#                   "lang" : "en",
#                   "value" : "Semester weekly hours"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "value" : "2"
#       } ],
#       "lvCreditsEnabled" : true,
#       "eLearningActive" : false
#    }, {
#       "id" : 950691822,
#       "courseNumber" : {
#          "dotIndex" : 0,
#          "databaseValue" : "0000002558",
#          "courseNumber" : "0000002558"
#       },
#       "semesterDto" : {
#          "id" : 198,
#          "key" : "23S",
#          "academicYearId" : 1615,
#          "semesterType" : "S",
#          "semesterDesignation" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "Summer semester 2023",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "Sommersemester 2023"
#                }, {
#                   "lang" : "en",
#                   "value" : "Summer semester 2023"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "startOfAcademicSemester" : {
#             "coType" : "date",
#             "value" : "2023-04-01"
#          },
#          "endOfAcademicSemester" : {
#             "coType" : "date",
#             "value" : "2023-09-30"
#          },
#          "shortName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "2023 S",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "2023 S"
#                }, {
#                   "lang" : "en"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          }
#       },
#       "courseTitle" : {
#          "coType" : "model-core.lib.model.langdata",
#          "value" : "Causal Inference in Time series (CIT4230006)",
#          "translations" : {
#             "translation" : [ {
#                "lang" : "de",
#                "value" : "Causal Inference in Time Series (CIT4230006)"
#             }, {
#                "lang" : "en",
#                "value" : "Causal Inference in Time series (CIT4230006)"
#             }, {
#                "lang" : "fr"
#             }, {
#                "lang" : "it"
#             } ]
#          }
#       },
#       "courseTypeDto" : {
#          "id" : 17,
#          "key" : "VO",
#          "courseTypeName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "lecture",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "Vorlesung"
#                }, {
#                   "lang" : "en",
#                   "value" : "lecture"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "courseTypeShortName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "VO",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "VO"
#                }, {
#                   "lang" : "en",
#                   "value" : "VO"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "sort" : 10
#       },
#       "lectureships" : [ {
#          "id" : 10271934,
#          "courseId" : 950691822,
#          "identityLibDto" : {
#             "id" : 385410,
#             "personId" : 385410,
#             "obfuscated" : "11582B8747F1A812",
#             "firstName" : "Seyed Jalal",
#             "lastName" : "Etesami",
#             "gender" : "MALE",
#             "genderNrForTitle" : 1,
#             "businessCardLink" : {
#                "rel" : "related",
#                "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#                "name" : "IdentityLibDto",
#                "key" : "11582B8747F1A812"
#             }
#          },
#          "teachingFunction" : {
#             "id" : 1,
#             "key" : "L",
#             "name" : "Leiter*in"
#          }
#       }, {
#          "id" : 10271935,
#          "courseId" : 950691822,
#          "identityLibDto" : {
#             "id" : 385410,
#             "personId" : 385410,
#             "obfuscated" : "11582B8747F1A812",
#             "firstName" : "Seyed Jalal",
#             "lastName" : "Etesami",
#             "gender" : "MALE",
#             "genderNrForTitle" : 1,
#             "businessCardLink" : {
#                "rel" : "related",
#                "href" : "https://campus.tum.de/tumonline/ee/rest/pages/brm.pm.bc/business-card/11582B8747F1A812",
#                "name" : "IdentityLibDto",
#                "key" : "11582B8747F1A812"
#             }
#          },
#          "teachingFunction" : {
#             "id" : 2,
#             "key" : "V",
#             "name" : "Vortragende*r"
#          }
#       } ],
#       "displayMoreLectureships" : false,
#       "displayCourseRegistrationInfo" : false,
#       "courseNormConfigs" : [ {
#          "key" : "SST",
#          "shortName" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "SWS",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "SWS"
#                }, {
#                   "lang" : "en",
#                   "value" : "SWS"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "name" : {
#             "coType" : "model-core.lib.model.langdata",
#             "value" : "Semester weekly hours",
#             "translations" : {
#                "translation" : [ {
#                   "lang" : "de",
#                   "value" : "Semesterwochenstunden"
#                }, {
#                   "lang" : "en",
#                   "value" : "Semester weekly hours"
#                }, {
#                   "lang" : "fr"
#                }, {
#                   "lang" : "it"
#                } ]
#             }
#          },
#          "value" : "2"
#       } ],
#       "lvCreditsEnabled" : true,
#       "eLearningActive" : false
#    } ]
# }