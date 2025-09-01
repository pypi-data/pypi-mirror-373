#pragma once

#include <qlat-utils/timer.h>

namespace qlat
{  //

int get_field_init_from_env();

API inline int& get_field_init()
// qlat parameter
{
  static int t = get_field_init_from_env();
  return t;
}

API inline Long& get_max_field_shift_direct_msg_size()
{
  static Long size = 1024L * 1024L * 1024L;
  // static Long size = 16;
  return size;
}

API inline std::string& get_lock_location()
{
  static std::string path;
  return path;
}

}  // namespace qlat
