#pragma once

#ifndef AMULET_RESOURCE_PACK_EXPORT
    #if defined(WIN32) || defined(_WIN32)
        #ifdef ExportAmuletResourcePack
            #define AMULET_RESOURCE_PACK_EXPORT __declspec(dllexport)
        #else
            #define AMULET_RESOURCE_PACK_EXPORT __declspec(dllimport)
        #endif
    #else
        #define AMULET_RESOURCE_PACK_EXPORT
    #endif
#endif

#if !defined(AMULET_RESOURCE_PACK_EXPORT_EXCEPTION)
    #if defined(_LIBCPP_EXCEPTION)
        #define AMULET_RESOURCE_PACK_EXPORT_EXCEPTION __attribute__((visibility("default")))
    #else
        #define AMULET_RESOURCE_PACK_EXPORT_EXCEPTION
    #endif
#endif
