function(doc) {
  if (doc.type == "slot-info") {
    emit(doc.slot, doc.build_id);
  }
}
