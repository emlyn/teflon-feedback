(ns feedback.core
  (:require
   [somnium.congomongo :as m]
   [clojure.string :as s]))

(defn connect []
  (let [conn (m/make-connection "lipservice")]
    (m/set-connection! conn)))

(defn get-result [query id]
  (let [results (filter #(= id (:id %))
                        (get-in query [:response :body :results]))]
    (if (= 1 (count results))
      (first results)
      (println (format "No unique result for id %s: %s" id results)))))

(defn convert-query [query result pos]
  {:query (get-in query [:params :text])
   :document (:id result)
   :user (:who query)
   :timestamp (.getTime (:when query))
   :url (:url result)
   :title (:title result)
   :score (:score result)
   :pos pos})

(defn process-queries [queries]
  (for [query queries
        [result pos] (map vector
                          (get-in query [:response :body :results])
                          (iterate inc 0))]
    (convert-query query result pos)))

(defn convert-feedback [query event pos]
  (let [result (get-result query (:id event))]
    {:type "binary"
     :task "teflon-feedback"
     :query (get-in query [:params :text])
     :document (:id event)
     :relevant ({"rated-good" true
                 "rated-bad" false
                 "clicked" nil} (:event event))
     :user (:who query)
     :timestamp (.getTime (:when query))
     :url (:url result)
     :title (:title result)
     :score (:score result)
     :pos pos}))

(defn load-feedback []
  (m/fetch :feedback
           :where {:feedback {:$exists true}}))

(defn process-feedback [queries]
  (for [query queries
        [event pos] (map vector
                         (:feedback query)
                         (iterate inc 0))]
    (convert-feedback query event pos)))

(defn escape [s]
  (-> s
      (str)
      (s/replace #"[\t\n]" " ")
      #_(#(if (re-find #"\"" %)
          (format "\"%s\""
                  (s/replace % #"\"" "\"\""))
          %))))

(defn save-queries)

(defn save-data [results fname]
  (with-open [f (clojure.java.io/writer fname)]
    (let [cols (sort (keys (first results)))]
      (.write f (str (s/join "\t"
                             (map (comp (partial apply str) rest str)
                                  cols))
                     "\n"))
      (doseq [r results]
        (.write f (str (s/join "\t"
                               (map (comp escape r) cols))
                       "\n"))))))

(defn -main []
  (connect)
  (let [r (process-queries (m/fetch :feedback))]
    (save-data r "data/teflon-queries.csv")
    (println "Queries       " (count r)))
  (let [q (load-feedback)
        r (process-feedback q)]
    (save-data r "data/teflon-feedback.csv")
    (println "With feedback " (count q))
    (println "Feedbacks " (count r))
    (println "       up " (count (filter #(:relevant %) r)))
    (println "     down " (count (filter #(false? (:relevant %)) r)))
    (println "    click " (count (filter #(nil? (:relevant %)) r)))))
