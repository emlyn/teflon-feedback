(ns feedback.core
  (:require
   [somnium.congomongo :as m]))

(defn connect []
  (let [conn (m/make-connection "lipservice"
                                     :host "localhost"
                                     :port 27017)]
    (m/set-connection! conn)))

(defn get-result [query id]
  (let [results (filter #(= id (:id %))
                        (get-in query [:response :body :results]))]
    (if (= 1 (count results))
      (first results)
      (throw Exception. (format "Not 1 result for id %s: %s" id results)))))

(defn convert [event query]
  (let [result (get-result query (:id event))]
    {:type "binary"
     :task "teflon-feedback"
     :query (get-in query [:params :text])
     :document (:id event)
     :relevant ({"rated-good" true
                 "rated-bad" false} (:event event))
     :user (:who query)
     :timestamp (:when query)
     :url (:url result)
     :title (:title result)
     :score (:score result)}))

(defn run []
  (println "Total " (m/fetch-count :feedback))
  (let [queries (m/fetch :feedback
                         :where {:feedback {:$exists true}})]
    (println "With feedback " (count queries))
    (let [results (for [query queries
                        event (:feedback query)]
                    (convert event query))]
      (println "Feedbacks " (count results))
      results)))

(defn -main []
  (connect)
  (run))
