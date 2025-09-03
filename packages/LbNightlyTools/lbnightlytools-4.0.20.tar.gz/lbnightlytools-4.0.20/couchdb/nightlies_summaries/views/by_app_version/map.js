function (doc) {
  emit(doc.app_version, {app_name: doc.app_name, time_start: doc.time_start});
}
